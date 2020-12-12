import pytest

import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir)))


class TestDBRepository():
    from exceptions.db_exceptions import \
        VKinderCannotConnectToDBException, VKinderCannotInsert, VKinderCannotUpdateUserState, VKinderCannotUpdateSearchConditions
    from database.repository import Repository
    good_connect = 'postgresql://vkinder:1@localhost:5432/vkinder'

    def _create_clear_repository_with_1_record(self, user_id: int):
        repository = self.Repository(self.good_connect)
        repository._drop_structure()
        repository._create_structure()
        user_info = {"first_name": "first_name",
                     "hometown": "hometown", "relation": 3}
        repository.create_new_search_user(user_id, user_info)
        return repository

    def test_connection_success(self):
        repository = self.Repository(self.good_connect)
        assert str(repository) == self.good_connect

    def test_connection_failed(self):
        with pytest.raises(self.VKinderCannotConnectToDBException) as e_info:
            assert self.Repository("test")
            print(str(e_info))

    def test_need_to_create_structure(self):
        repository = self.Repository(self.good_connect)
        repository._drop_structure()
        assert repository._has_need_to_create() is True

    def test_no_need_to_create_structure(self):
        repository = self.Repository(self.good_connect)
        repository._drop_structure()
        repository._create_structure()
        assert repository._has_need_to_create() is False

    def test_create_new_search_user_full_info(self):
        repository = self.Repository(self.good_connect)
        repository._drop_structure()
        repository._create_structure()
        user_id = 111
        user_info = {"first_name": "first_name", "second_name": "second_name",
                     "hometown": "hometown", "age": 44, "sex": 2, "relation": 3}
        assert repository.create_new_search_user(user_id, user_info) is True

    def test_create_new_search_user_part_info(self):
        repository = self.Repository(self.good_connect)
        repository._drop_structure()
        repository._create_structure()
        user_id = 111
        user_info = {"first_name": "first_name",
                     "hometown": "hometown", "relation": 3}
        assert repository.create_new_search_user(user_id, user_info) is True

    def test_create_new_search_user_with_initial_state_0(self):
        repository = self.Repository(self.good_connect)
        repository._drop_structure()
        repository._create_structure()
        user_id = 111
        user_info = {"first_name": "first_name",
                     "hometown": "hometown", "relation": 3}
        repository.create_new_search_user(user_id, user_info)
        assert repository.get_state_of_search_user(user_id) == 0

    def test_update_status_change(self):
        repository = self.Repository(self.good_connect)
        repository._drop_structure()
        repository._create_structure()
        user_id = 111
        excpected = 5
        user_info = {"first_name": "first_name",
                     "hometown": "hometown", "relation": 3}
        repository.create_new_search_user(user_id, user_info)
        repository.set_state_of_search_user(user_id, excpected)
        assert repository.get_state_of_search_user(user_id) == excpected

    def test_get_text_choose_sex(self):
        repository = self.Repository(self.good_connect)
        actual = [('0 - not specified',), ('1 - female',), ('2 - male',)]
        expected = repository.get_text_choose_sex()
        assert actual == expected

    def test_create_new_condition(self):
        user_id = 111
        repository = self._create_clear_repository_with_1_record(user_id)
        repository.create_new_condition(user_id)
        actual = repository.get_exists_opened_condition(user_id)
        non_expected = None
        assert actual != non_expected

    def test_add_search_condition_sex_succesfull(self):
        user_id = 111
        repository = self._create_clear_repository_with_1_record(user_id)
        repository.create_new_condition(user_id)
        expected = True
        assert expected == repository.add_search_condition(user_id, "sex", 1)

    def test_add_search_condition_sex_failed(self):
        user_id = 111
        repository = self._create_clear_repository_with_1_record(user_id)
        repository.create_new_condition(user_id)
        expected = True
        with pytest.raises(self.VKinderCannotUpdateSearchConditions) as e_info:
            assert expected == repository.add_search_condition(
                user_id, "sex", 5)

    def test_add_search_condition_age_succesfull(self):
        user_id = 111
        repository = self._create_clear_repository_with_1_record(user_id)
        repository.create_new_condition(user_id)
        expected = True
        assert expected == repository.add_search_condition(user_id, "age", 40)

    def test_add_search_condition_age_failed(self):
        user_id = 111
        repository = self._create_clear_repository_with_1_record(user_id)
        repository.create_new_condition(user_id)
        expected = True
        with pytest.raises(self.VKinderCannotUpdateSearchConditions) as e_info:
            assert expected == repository.add_search_condition(
                user_id, "age", 1.5)

    def test_add_search_condition_age_from_succesfull(self):
        user_id = 111
        repository = self._create_clear_repository_with_1_record(user_id)
        repository.create_new_condition(user_id)
        expected = True
        assert expected == repository.add_search_condition(
            user_id, "age_from", 40)

    def test_add_search_condition_age_from_failed(self):
        user_id = 111
        repository = self._create_clear_repository_with_1_record(user_id)
        repository.create_new_condition(user_id)
        expected = True
        with pytest.raises(self.VKinderCannotUpdateSearchConditions) as e_info:
            assert expected == repository.add_search_condition(
                user_id, "age_from", 1.5)

