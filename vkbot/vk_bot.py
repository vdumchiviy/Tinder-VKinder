from random import randrange
import sys
import os.path
# from datetime import date
import datetime
# import time
# from time import strftime, strptime
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType


sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir)))


class VK_Bot():

    from exceptions.vk_bot_exceptions import VKBotNoTokenGiven
    from repository.repository import Repository

    def __init__(self, token: str = "", test_mode: bool = False):
        if token:
            self.test_mode = test_mode
            self.vk_session = vk_api.VkApi(token=token)
            self.long_poll = VkLongPoll(self.vk_session)
            self.repository = self.Repository()
        else:
            raise self.VKBotNoTokenGiven(f"No token was given")

    def _send_message(self, user_id: int, message: str):
        self.vk_session.method('messages.send', {
            'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7), })

    def _repository_hard_reset(self):
        self.repository._hard_reset()

    def _get_age(self, date_str: str):
        try:
            birth_date = datetime.datetime.strptime(
                date_str, '%d.%m.%Y').date()
        except Exception:
            return 0
        today = datetime.datetime.now().date()
        age = today.year - birth_date.year
        full_year_passed = (today.month, today.day) < (
            birth_date.month, birth_date.day)
        if full_year_passed:
            age -= 1
        return age

    def _get_vk_user_information(self, user_id: int):
        if self.test_mode:
            self._send_message(
                user_id, f'_get_vk_user_information(user_id = {user_id})')
        response = self.vk_session.method('users.get',
                                          {'user_id': user_id,
                                           'fields': 'first_name,last_name,sex,bdate,home_town,photo_50,relation'})
        result = response[0]
        age = self._get_age(result.get("bdate"))
        result["age"] = age

        return result

    def _check_new_user(self, user_id: int):
        if self.test_mode:
            self._send_message(
                user_id, f'__check_new_user(user_id = {user_id})')
        if self.repository.has_user_exists(user_id):
            result = True
        else:
            user_info = self._get_vk_user_information(user_id)
            if self.test_mode:
                self._send_message(
                    user_id, f'__check_new_user. user_info = {user_info})')
            result = self.repository.create_new_search_user(user_id, user_info)

        if self.test_mode:
            self._send_message(
                user_id, f'__check_new_user. result = {result})')
        return result

    def get_user_state(self, user_id):
        self._check_new_user(user_id)
        return self.repository.get_user_state(user_id)

    def _search_pair(self, user_id: int):
        self.repository.check_new_user(user_id)
        self._send_message(user_id, '_search_pair()')

    def _erase_search_settings(self, user_id: int):
        self._send_message(user_id, '_erase_search_settings()')

    def _set_age_from(self, user_id: int):
        self._send_message(user_id, '__set_age_from()')

    def _set_age_to(self, user_id: int):
        self._send_message(user_id, '__set_age_to()')

    def _ask_age(self, user_id: int, next_user_state: int):
        if self.test_mode:
            self._send_message(user_id, '_ask_age()')
        self.repository.set_user_state(user_id, next_user_state)
        self._send_message(user_id, 'Enter exact age:')

    def _set_age(self, user_id: int, entered_text):
        if self.test_mode:
            self._send_message(
                user_id, f'__set_age(user_id={user_id},entered_text={entered_text})')
        self.repository.add_search_condition(user_id, 'age', entered_text)

    def _ask_sex(self, user_id: int, next_user_state: int):
        if self.test_mode:
            self._send_message(user_id, '_ask_sex()')
        self.repository.set_user_state(user_id, next_user_state)
        self._send_message(user_id, 'Enter sex code for find:')
        sexes = self.repository.get_text_choose_sex()
        for sex in sexes:
            self._send_message(user_id, str(sex))

    def _set_sex(self, user_id: int, entered_text):
        if self.test_mode:
            self._send_message(
                user_id, f'__set_sex(user_id={user_id},entered_text={entered_text})')
        self.repository.add_search_condition(user_id, 'sex', entered_text)

    known_commands = \
        {'search': ['search pair', _search_pair, 0],
         'new': ['erase search settings', _erase_search_settings, 0],
         'set age from': ['set minimal age for searching', _set_age_from, 2],
         'set age to': ['set maximum age for searching', _set_age_to, 3],
         'set age': ['set exact age for searching', _ask_age, 1],
         'set sex': ['set exact sex for searching', _ask_sex, 5]
         }
    known_inside_states = \
        {5: [_set_sex],
         }

    def _get_known_command(self, input_command: str):
        try:
            return self.known_commands[input_command]
        except Exception:
            return None

    def _get_known_states(self, input_state: int):
        try:
            return self.known_inside_states[input_state]
        except Exception:
            return None

    def _show_known_commands(self, user_id: int):
        self._send_message(user_id, str(self.known_commands))

    def conversation(self):

        for event in self.long_poll.listen():

            if event.type == VkEventType.MESSAGE_NEW:

                if event.to_me:
                    request = event.text
                    if request == 'stop':
                        return
                    self._check_new_user(event.user_id)

                    command = self._get_known_command(request)
                    if command:
                        self._send_message(event.user_id, str(command))
                        # description = command[0]
                        new_state = command[2]
                        func = command[1]
                        func(self, event.user_id, new_state)
                    else:
                        current_user_state = self.repository.get_user_state(
                            event.user_id)
                        command_state = self._get_known_states(
                            current_user_state)
                        if command_state:
                            func = command_state[0]
                            func(self, event.user_id, request)

                        else:
                            self._send_message(
                                event.user_id, "Неизвестная команда")
                            self._show_known_commands(event.user_id)


def get_vk_token():
    path = os.path.abspath(os.path.join(
        os.path.abspath(os.path.realpath(".")), "resources", "vkinder_key.ini"))
    with open(path, "r") as file:
        return file.read()


def calculate_age(birth_date):
    today = datetime.datetime.now().date()
    age = today.year - birth_date.year
    full_year_passed = (today.month, today.day) < (
        birth_date.month, birth_date.day)
    if full_year_passed:
        age -= 1
    return age


if __name__ == "__main__":
    # path=os.path.abspath(os.path.join(
    #     os.path.abspath(os.path.realpath("."), "resources", "vkinder_key.ini"))
    # print(path)
    # birth = datetime.datetime.strptime('07.12.1976', '%d.%m.%Y').date()
    # birth = datetime.datetime.strptime('11.17', '%d.%m.%Y').date()
    # age = calculate_age(birth)
    # print(age)
    vk_bot = VK_Bot(get_vk_token(), test_mode=True)
    vk_bot._repository_hard_reset()
    # print(vk_bot._check_new_user(35163310))
    # print(vk_bot._get_vk_user_information(3317276))
    # print(vk_bot._get_vk_user_information(1749874))
    vk_bot.conversation()
