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
        if not self.repository.has_user_condition_exists(user_id):
            self._send_message(user_id, "Search condition isn't exists")
            return False
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

        results_to_save = search_result["items"]

        if not results_to_save:
            self._send_message(
                user_id, 'Поиск не дал результатов, попробуйте изменить условия.')
            return None

        for item in results_to_save:
            item['age'] = self._get_age(item['bdate'])
            item['city'] = item.get('home_town')
            item = self._get_user_photo_info(item['id'], item)
        result = self.repository.save_search_result(user_id, results_to_save)
        self.repository.set_user_state(user_id, next_user_state)
        result = self._ask_pair(user_id)

        return result

    def _get_user_photo_info(self, pair_id: int, pair_info: dict):
        params = {"user_id": pair_id, "album_id": 'profile',
                  "extended": 1, "photo_sizes": 1, "rev": 1}
        request = self.vkuser_session.method('photos.get', params)
        if request['count'] != 0:
            photos = request['items']
            images = dict()
            for photo in photos:
                images[photo['sizes'][0]['url']] = photo['likes']['count']

            images_list = list(images.items())
            images_list.sort(key=lambda i: i[1], reverse=True)

            three_or_less = (3 if len(images_list) >= 3 else len(images_list))
            for i in range(three_or_less):
                pair_info['photo'+str(i+1)] = images_list[i][0]
                pair_info['likes'+str(i+1)] = images_list[i][1]

        return pair_info

    def _begin_new_search_settings(self, user_id: int, next_user_state: int):
        if self.test_mode:
            self._send_message(user_id, '_begin_new_search_settings()')
        self.repository.begin_new_search_settings(user_id)
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
        self._send_message(user_id, f'Age min limit was setted')

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
        self._send_message(user_id, f'Age max limit was setted')

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
        self._send_message(user_id, f'Age was setted')

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
        self._send_message(user_id, f'Sex was setted')

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
        self._send_message(user_id, f'Relation was setted')

    def _print_pair(self, user_id: int, pair: dict):
        self._send_message(user_id, str(pair))

    def _ask_pair(self, user_id: int):
        pair = self.repository.get_next_saved_pair(user_id)
        if not pair:
            self.repository.set_user_state(user_id, 0)
            return None
        self._print_pair(user_id, pair)
        self._send_message(
            user_id, "Add user ? (y)es / (n)o / to (b)lacklist / (c)ancel")
        self.repository.set_user_state(user_id, 15)

    def _set_pair(self, user_id: int, entered_text: str):
        if entered_text == 'y':
            self.repository.add_pair(user_id)
            self.repository.set_last_pair_to_offered_status(user_id)
            self.repository.set_user_state(user_id, 11)
            self._send_message(user_id, "Pair was added")
            self._ask_pair(user_id)
        elif entered_text == 'n':
            self.repository.set_last_pair_to_offered_status(user_id)
            self.repository.set_user_state(user_id, 11)
            self._send_message(user_id, "Pair wasn't added")
            self._ask_pair(user_id)
        elif entered_text == 'b':
            self.repository.add_pair_to_blacklist(user_id)
            self.repository.set_last_pair_to_offered_status(user_id)
            self.repository.set_user_state(user_id, 11)
            self._send_message(user_id, "Pair was added to blacklist")
            self._ask_pair(user_id)
        elif entered_text == 'c':
            self.repository.set_all_pairs_to_offered_status(user_id)
            self.repository.set_user_state(user_id, 0)
            self._send_message(user_id, "Canceled")
        else:
            self._send_message(user_id, "=Unknown choise=")
            self._send_message(
                user_id, "Add user ? (y)es / (n)o / to (b)lacklist / (c)ancel")

    def _show_all_pairs(self, user_id: int, next_user_state: int):
        pairs = self.repository.get_all_pairs(user_id)
        if pairs:
            for pair in pairs:
                self._print_pair(user_id, pair)
        else:
            self._send_message(user_id, "You haven't pairs")
        self.repository.set_user_state(user_id, next_user_state)

    def _show_all_blaclist_pairs(self, user_id: int, next_user_state: int):
        pairs = self.repository.get_all_blacklist_pairs(user_id)
        if pairs:
            for pair in pairs:
                self._print_pair(user_id, pair)
        else:
            self._send_message(user_id, "You haven't blaclist pairs")
        self.repository.set_user_state(user_id, next_user_state)

    def _ask_delete_pair(self, user_id: int, next_user_state: int):
        self._send_message(
            user_id, "Enter then number of pair what you want to delete:")
        self.repository.set_user_state(user_id, next_user_state)

    def _delete_pair(self, user_id: int, entered_text: str):
        result = self.repository.delete_pair(user_id, entered_text)
        if result:
            self._send_message(user_id, f"Pair {entered_text} was deleted")
        else:
            self._send_message(user_id, f"Pair {entered_text} wasn't deleted")
        return result

    known_commands = \
        {'search': ['search pair', _search_pair, 11],
         'new': ['begin new search settings', _begin_new_search_settings, 0],
         'set age from': ['set minimal age for searching', _ask_age_from, 2],
         'set age to': ['set maximum age for searching', _ask_age_to, 3],
         'set age': ['set exact age for searching', _ask_age, 1],
         'set sex': ['set exact sex for searching', _ask_sex, 5],
         'set relation': ['set relation for searching', _ask_relation, 8],
         'list': ['list all pairs', _show_all_pairs, 0],
         'del': ['delete pair', _ask_delete_pair, 25],
         'blacklist': ['list all blacklist pair', _show_all_blaclist_pairs, 0]
         }
    known_inside_states = \
        {5: [_set_sex],
         1: [_set_age],
         2: [_set_age_from],
         3: [_set_age_to],
         8: [_set_relation],
         15: [_set_pair],
         25: [_delete_pair]
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
        message = 'You can use:\n===============\n'
        self._send_message(user_id, 'You can use:')
        for command, item in self.known_commands.items():
            message = message + f'{command}: {item[0]}\n'
        self._send_message(user_id, message)

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
                                event.user_id, "Unknown command")
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
    vk_bot = VK_Bot(get_vk_token("vkinder_key.ini"),
                    get_vk_token("vkuser_key.ini"), test_mode=True)
    vk_bot._repository_hard_reset()
    vk_bot.conversation()
