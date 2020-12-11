import pytest

import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir)))


class TestDBRepository():
    from exceptions.db_exceptions import \
        VKinderCannotConnectToDBException, VKinderCannotInsert, VKinderCannotUPdateUserState
    from database.repository import Repository
    good_connect = 'postgresql://vkinder:1@localhost:5432/vkinder'

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
        assert repository.get_user_state_id(user_id) == 0

    def test_update_status_change(self):
        repository = self.Repository(self.good_connect)
        repository._drop_structure()
        repository._create_structure()
        user_id = 111
        excpected = 5
        user_info = {"first_name": "first_name",
                     "hometown": "hometown", "relation": 3}
        repository.create_new_search_user(user_id, user_info)
        repository.update_state_search_user(user_id, excpected)
        assert repository.get_user_state_id(user_id) == excpected
