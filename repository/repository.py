
import sys
import os.path

sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir)))


class Repository():
    from exceptions.repository_exceptions import VKinderModeNotFoundException, VKinderCannotDeletePair

    def __init__(self, mode: str = "postgresql",
                 settings: dict = {'host': 'localhost', 'port': 5432, 'base': 'vkinder',
                                   'user': 'vkinder', 'password': '1'}, test_mode: bool = False):

        self.mode = mode
        if mode == "postgresql":
            from database.repository import Repository
            self.connection_string = \
                f'{mode}://{settings["user"]}:{settings["password"]}' \
                + f'@{settings["host"]}:{settings["port"]}/{settings["base"]}'
            self.repository = Repository(self.connection_string, test_mode)
        else:
            raise self.VKinderModeNotFoundException(
                f"Repository's mode not found: {mode:}")

    def __str__(self):
        if self.mode == "postgresql":
            return self.connection_string
        else:
            return "unknown settings"

    def get_repository_user(self):
        result = self.repository.get_repository_user()[0][0]
        return result

    def has_user_exists(self, user_id: int):
        return self.repository.has_user_exists(user_id)

    def has_user_condition_exists(self, user_id: int):
        return self.repository.has_user_condition_exists(user_id)

    def get_search_conditions(self, user_id: int):
        return self.repository.get_search_conditions(user_id)

    def create_new_search_user(self, user_id: int, user_info: dict):
        return self.repository.create_new_search_user(user_id, user_info)

    def get_user_state(self, user_id: int):
        return self.repository.get_state_of_search_user(user_id)

    def set_user_state(self, user_id: int, new_state: int):
        return self.repository.set_state_of_search_user(user_id, new_state)

    def get_text_choose_sex(self):
        return self.repository.get_text_choose_sex()

    def get_text_choose_relation(self):
        return self.repository.get_text_choose_relation()

    def add_search_condition(self, user_id: int, search_criteria: str, value: str):
        self.repository.add_search_condition(user_id, search_criteria, value)

    def _hard_reset(self):
        return self.repository._hard_reset()

    def save_search_result(self, user_id: int, results_to_save: list):
        return self.repository.save_search_result(user_id, results_to_save)

    def get_next_saved_pair(self, user_id: int):
        return self.repository.get_next_saved_pair(user_id)

    def set_last_pair_to_offered_status(self, user_id: int):
        return self.repository.set_last_pair_to_offered_status(user_id)

    def set_all_pairs_to_offered_status(self, user_id: int):
        return self.repository.set_all_pairs_to_offered_status(user_id)

    def add_pair(self, user_id: int):
        return self.repository.add_pair(user_id)

    def add_pair_to_blacklist(self, user_id: int):
        return self.repository.add_pair_to_blacklist(user_id)

    def begin_new_search_settings(self, user_id: int):
        return self.repository.begin_new_search_settings(user_id)

    def get_all_pairs(self, user_id: int):
        return self.repository.get_all_pairs(user_id)

    def get_all_blacklist_pairs(self, user_id: int):
        return self.repository.get_all_blacklist_pairs(user_id)

    def delete_pair(self, user_id: int, pair_number: int):
        try:
            return self.repository.delete_pair(user_id, pair_number)
        except self.VKinderCannotDeletePair:
            return False


def a():
    print("repository hello")
    repository = Repository(mode="kjh")
    print(repository.get_repository_user())


if __name__ == "__main__":
    a()
