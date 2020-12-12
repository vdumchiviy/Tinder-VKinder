import pytest
import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir)))


class TestVKBot():
    from exceptions.vk_bot_exceptions import VKBotNoTokenGiven
    from vkbot.vk_bot import VK_Bot

    def setup(self):
        path = os.path.abspath(os.path.join(
            os.path.abspath(os.path.realpath(".")), "resources", "vkinder_key.ini"))
        with open(path, "r") as file:
            self.token = file.read()
        self.vk_bot = self.VK_Bot(self.token)

    def test_new_user(self):
        expected = True
        assert self.vk_bot._check_new_user(35163310) == expected


# if __name__ == "__main__":
#     path = os.path.abspath(os.path.join(
#         os.path.abspath(os.path.realpath(".")), "resources", "vkinder_key.ini"))
#     print(path)
