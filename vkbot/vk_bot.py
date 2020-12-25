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

    def __init__(self, token: str = "", vkuser_token: str = "", test_mode: bool = False):
        if token and vkuser_token:
            self.test_mode = test_mode
            self.vk_session = vk_api.VkApi(token=token)
            self.long_poll = VkLongPoll(self.vk_session)
            self.vkuser_session = vk_api.VkApi(token=vkuser_token)
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

    def _search_pair_with_conditions(user_id: int, conditions: dict):
        pass

    def _search_pair(self, user_id: int, next_user_state: int):
        if self.test_mode:
            self._send_message(user_id, '_search_pair()')
        self._check_new_user(user_id)
        self.repository.has_user_condition_exists(user_id)
        conditions = self.repository.get_search_conditions(user_id)
        # self._search_pair_with_conditions(user_id, conditions)
        # params = {'user_id': user_id}
        params = dict()
        params['count'] = 5
        params['fields'] = 'first_name,last_name,sex,bdate,home_town,photo_50,relation'
        params['sex'] = conditions['sex']
        params['status'] = conditions['relation']
        params['age_from'] = conditions['age_from']
        params['age_to'] = conditions['age_to']
        if conditions.get('city'):
            params['hometown'] = conditions['city']

        search_result = self.vkuser_session.method('users.search', params)
        if not search_result:
            self._send_message(
                user_id, 'Поиск не дал результатов, попробуйте изменить условия.')
            return None
        results_to_save = search_result["items"]
        for item in results_to_save:
            item['age'] = self._get_age(item['bdate'])
            item['city'] = item['home_town']
        result = self.repository.save_search_result(user_id, results_to_save)
        self.repository.set_user_state(user_id, next_user_state)
        result = self._ask_pair(user_id)

        return result

    def _erase_search_settings(self, user_id: int, next_user_state: int):
        if self.test_mode:
            self._send_message(user_id, '_erase_search_settings()')
        self.repository.set_user_state(user_id, next_user_state)

    def _ask_age_from(self, user_id: int, next_user_state: int):
        if self.test_mode:
            self._send_message(user_id, '_ask_age_from()')
        self.repository.set_user_state(user_id, next_user_state)
        self._send_message(user_id, 'Enter age from:')

    def _set_age_from(self, user_id: int, entered_text):
        if self.test_mode:
            self._send_message(
                user_id, f'__set_age_from(user_id={user_id},entered_text={entered_text})')
        self.repository.add_search_condition(user_id, 'age_from', entered_text)
        self.repository.set_user_state(user_id, 0)

    def _ask_age_to(self, user_id: int, next_user_state: int):
        if self.test_mode:
            self._send_message(user_id, '_ask_age_to()')
        self.repository.set_user_state(user_id, next_user_state)
        self._send_message(user_id, 'Enter age till:')

    def _set_age_to(self, user_id: int, entered_text):
        if self.test_mode:
            self._send_message(
                user_id, f'__set_age_to(user_id={user_id},entered_text={entered_text})')
        self.repository.add_search_condition(user_id, 'age_to', entered_text)
        self.repository.set_user_state(user_id, 0)

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
        self.repository.set_user_state(user_id, 0)

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
        self.repository.set_user_state(user_id, 0)

    def _ask_relation(self, user_id: int, next_user_state: int):
        if self.test_mode:
            self._send_message(user_id, '_ask_relation()')
        self.repository.set_user_state(user_id, next_user_state)
        self._send_message(user_id, 'Enter relation code for find:')
        sexes = self.repository.get_text_choose_relation()
        for sex in sexes:
            self._send_message(user_id, str(sex))

    def _set_relation(self, user_id: int, entered_text):
        if self.test_mode:
            self._send_message(
                user_id, f'__set_relation(user_id={user_id},entered_text={entered_text})')
        self.repository.add_search_condition(user_id, 'relation', entered_text)
        self.repository.set_user_state(user_id, 0)

    def _print_pair(self, user_id: int, pair: dict):
        self._send_message(user_id, str(pair))

    def _ask_pair(self, user_id: int):
        pair = self.repository.get_next_saved_pair(user_id)
        if not pair:
            self.repository.set_user_state(user_id, 0)
            return None
        self._print_pair(user_id, pair)
        self._send_message(user_id, "Add user to favorite? (y/n)")
        self.repository.set_user_state(user_id, 15)

    def _set_pair(self, user_id: int, entered_text: str):
        if entered_text == 'y':
            self.repository.add_pair(user_id)
            self.repository.set_last_pair_to_offered_status(user_id)
            self.repository.set_user_state(user_id, 11)
            self._ask_pair(user_id)
        elif entered_text == 'n':
            self._send_message(user_id, "Pair wasn't added")
            self.repository.set_last_pair_to_offered_status(user_id)
            self.repository.set_user_state(user_id, 11)
            self._ask_pair(user_id)
        else:
            self._send_message(user_id, "=Unknown choise=")
            self._send_message(user_id, "Add user to favorite? (y/n)")

    known_commands = \
        {'search': ['search pair', _search_pair, 11],
         'new': ['erase search settings', _erase_search_settings, 0],
         'set age from': ['set minimal age for searching', _ask_age_from, 2],
         'set age to': ['set maximum age for searching', _ask_age_to, 3],
         'set age': ['set exact age for searching', _ask_age, 1],
         'set sex': ['set exact sex for searching', _ask_sex, 5],
         'set relation': ['set relation for searching', _ask_relation, 8]

         }
    known_inside_states = \
        {5: [_set_sex],
         1: [_set_age],
         2: [_set_age_from],
         3: [_set_age_to],
         8: [_set_relation],
         15: [_set_pair]
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


def get_vk_token(file_name_with_token: str):
    path = os.path.abspath(os.path.join(
        os.path.abspath(os.path.realpath(".")), "resources", file_name_with_token))
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
    vk_bot = VK_Bot(get_vk_token("vkinder_key.ini"),
                    get_vk_token("vkuser_key.ini"), test_mode=True)
    vk_bot._repository_hard_reset()
    # print(vk_bot._check_new_user(35163310))
    # print(vk_bot._get_vk_user_information(3317276))
    # print(vk_bot._get_vk_user_information(1749874))
    vk_bot.conversation()
