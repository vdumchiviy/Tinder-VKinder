import pytest

import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir)))


class TestRepository():
    from repository.repository import Repository
    from exceptions.repository_exceptions import VKinderModeNotFoundException

    def test_creation_with_wrong_mode(self):
        with pytest.raises(self.VKinderModeNotFoundException) as e_info:
            assert self.Repository(mode="test")
            print(str(e_info))

    def test_connection_local_postgresql(self):
        repository = self.Repository()
        assert str(repository) == 'postgresql://vkinder:1@localhost:5432/vkinder'
