# from repository import repository
# from database import repository
from repository.repository import Repository
from vkbot.vk_bot import VK_Bot
import vk_api

import os.path


def get_vk_token():
    path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "resources", "vkinder_key.ini"))

    with open(path, "r") as file:
        return file.read()


def main():
    vk_token = get_vk_token()
    vk_session = vk_api.VkApi(token=vk_token)
    # vk = vk_session.get_api()
    response = vk_session.method('users.search', {
                                 'q': 'Ковтун Максим', 'sex': 2, 'age_from': 1, 'age_to': 45, 'hometown': 'Москва'})
    print(response)
    return

    repository = Repository()
    print(repository.get_repository_user())


if __name__ == "__main__":
    vk_bot = VK_Bot(get_vk_token())


# t = {}  # создаем словарь для хранения данных, получаемых от API VK
# for j in range(0, len(data)):  # запускаем поиск по массиву
#     # Далее следует обращение к API с нашими параметрами:
#     t[j] = vk.users.search(q=data[‘N’][j] + ‘ ‘ + data[‘F’][j], birth_day=data[‘D’][j],
#                            birth_month=data[‘M’][j], birth_year=data[‘Y’][j], count=1000, fields=’bdate, city’)
#     for h in (t[j][‘items’]):
#         # Сохраняем результаты поиска в файл”users.txt”
#         with open(‘users.txt’, ’a’) as f1:
#             f1.write((str(data[‘id’][j]) + ‘
#                       ’  # ID исходный
#                       + str(t[j][‘count’]) + ‘
#                       ’  # Количество найденных пользователей
#                       + str(h[‘id’]) + ‘
#                       ’  # ID пользователя VK
#                       + h[‘last_name’] + ‘
#                       ’  # Фамилия
#                       + h[‘first_name’] + ‘
#                       ’  # Имя
#                       + h.get(‘bdate’, ’’) + ‘
#                       ’  # Дата рождения
#                       # У города несколько параметров — нам нужно название: title
#                       + h.get(‘city’, {}).get(‘title’, ’’)
#                       + ‘
#                       \n’).encode(‘cp1251’, ‘replace’).decode(‘cp1251’))
#     # Для удаления нестандартных символов, которые могут вызывать ошибки
