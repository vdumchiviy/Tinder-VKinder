import sqlalchemy
import sys
import os.path
import os


sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir)))


class Repository():
    from exceptions.db_exceptions import \
        VKinderCannotConnectToDBException, VKinderCannotInsert, VKinderCannotUPdateUserState

    def _has_need_to_create(self):
        try:
            result = self.db_conn.execute(
                "select count(*) from spr_sexes").fetchone()
            if result[0] > 0:
                return False
            return True
        except Exception:
            return True

    def _drop_structure(self):
        path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "00_DROP.sql"))
        with open(path, "r") as file:
            sql_file = file.read()
            for SQL in sql_file.split(";"):
                with self.db_conn.begin():
                    if SQL:
                        self.db_conn.execute(SQL)

    def _create_structure(self):
        path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "01_CREATE.sql"))
        with open(path, "r") as file:
            sql_file = file.read()
            for SQL in sql_file.split(";"):
                with self.db_conn.begin():
                    if SQL:
                        self.db_conn.execute(SQL)
        path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "02_SPR_INSERT.sql"))
        with open(path, "r") as file:
            sql_file = file.read()
            for SQL in sql_file.split(";"):
                if SQL:
                    self.db_conn.execute(SQL)

    def __init__(self, connection_string: str, echo_flag: bool = False):
        try:
            self.db_engine = sqlalchemy.create_engine(
                connection_string, echo=echo_flag)
            self.db_conn = self.db_engine.connect()
            if self._has_need_to_create():
                self._drop_structure()
                self._create_structure()
            self.connection_string = connection_string
        except Exception as e:
            raise self.VKinderCannotConnectToDBException(
                "Cannot connect to DB: " + str(e))

    def has_user_exists(self, user_id: int):
        result = self.db_conn.execute("""
            select (case when count(*) > 0 then true else false end) as res
            from vkinder_search_user where vk_id = %s""", (user_id)).fetchone()
        return result[0]

    def get_state_of_search_user(self, user_id: int):
        result = self.db_conn.execute("""
            select user_state from vkinder_search_user where vk_id = %s""", (user_id)).fetchone()
        return result[0]

    def _get_current_schema(self):
        return self.db_conn.execute("select current_schema()").fetchall()

    def get_repository_user(self):
        return self.db_conn.execute("select current_user").fetchall()

    def __str__(self):
        return self.connection_string

    def create_new_search_user(self, user_id: int, user_info: dict):
        SQL = sqlalchemy.text(
            """insert into vkinder_search_user
            (vk_id, first_name, second_name, city, age, sex, relation, user_state)
            values (:vk_id, :first_name, :second_name, :city, :age, :sex, :relation, :user_state)""")
        params = {"vk_id": user_id, "first_name": user_info.get("first_name"),
                  "second_name": user_info.get("second_name"), "city": user_info.get("hometown"),
                  "age": user_info.get("age"), "sex": user_info.get("sex"),
                  "relation": user_info.get("relation"), "user_state": 0}
        try:
            # self.db_conn.execute(SQL)
            self.db_engine.execute(SQL, params)
        except Exception as e:
            raise self.VKinderCannotInsert(
                f"Error during insert new search user with id {user_id} " + str(e))
        return True

    def set_state_of_search_user(self, user_id: int, new_state: int):
        SQL = sqlalchemy.text(
            """update vkinder_search_user
            set user_state = :user_state
            where vk_id = :vk_id""")
        params = {"vk_id": user_id, "user_state": new_state}
        try:
            # self.db_conn.execute(SQL)
            self.db_engine.execute(SQL, params)
        except Exception as e:
            raise self.VKinderCannotUPdateUserState(
                f"Error during update user state {new_state} of search user with id {user_id} " + str(e))
        return True

    def get_text_choose_sex(self):
        result = self.db_conn.execute("""
            select sex_id||' - '||sex_nm from spr_sexes order by 1""").fetchall()
        return result

    def _hard_reset(self):
        self._drop_structure()
        self._create_structure()


if __name__ == "__main__":
    repository = Repository(
        'postgresql://vkinder:1@localhost:5432/vkinder', True)
    print(repository.get_text_choose_sex())
    # repository._drop_structure()
    # repository._create_structure()
    # print(repository.get_repository_user())
    # print(repository.has_user_exists(4))
