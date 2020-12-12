
import sys
import os.path

sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir)))


class Repository():

    def __init__(self, mode: str = "postgresql",
                 settings: dict = {'host': 'localhost', 'port': 5432, 'base': 'vkinder',
                                   'user': 'vkinder', 'password': '1'}, test_mode: bool = False):
        from exceptions.repository_exceptions import VKinderModeNotFoundException

        self.mode = mode
        if mode == "postgresql":
            from database.repository import Repository
            self.connection_string = \
                f'{mode}://{settings["user"]}:{settings["password"]}' \
                + f'@{settings["host"]}:{settings["port"]}/{settings["base"]}'
            self.repository = Repository(self.connection_string, test_mode)
        else:
            raise VKinderModeNotFoundException(
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

    def create_new_search_user(self, user_id: int, user_info: dict):
        return self.repository.create_new_search_user(user_id, user_info)

    def get_user_state(self, user_id: int):
        return self.repository.get_state_of_search_user(user_id)

    def set_user_state(self, user_id: int, new_state: int):
        return self.repository.set_state_of_search_user(user_id, new_state)

    def get_text_choose_sex(self):
        return self.repository.get_text_choose_sex()

    def add_search_condition(self, user_id: int, search_criteria: str, value: str):
        self.repository.add_search_condition(user_id, search_criteria, value)

    def _hard_reset(self):
        self.repository._hard_reset()


def a():
    print("repository hello")
    repository = Repository(mode="kjh")
    print(repository.get_repository_user())


if __name__ == "__main__":
    a()
