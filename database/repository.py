import sqlalchemy
import sys
import os.path
import os


sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir)))


class Repository():
    from exceptions.db_exceptions import \
        VKinderCannotConnectToDBException, VKinderCannotInsert, VKinderCannotUpdateUserState, \
        VKinderCannotUpdateSearchConditions, VKinderCannotInsertSearchedResults, VKinderCannotAddNewPair, \
        VKinderCannotUPdateIsOfferedStatusOfPair

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
            self.search_fields = \
                {"sex": "sex", "age": "age_range", "age_from": "age_range",
                 "age_to": "age_range", "relation": "relation"}
        except Exception as e:
            raise self.VKinderCannotConnectToDBException(
                "Cannot connect to DB: " + str(e))

    def has_user_exists(self, user_id: int):
        result = self.db_conn.execute("""
            select (case when count(*) > 0 then true else false end) as res
            from vkinder_search_user where vk_id = %s""", (user_id)).fetchone()
        return result[0]

    def has_user_condition_exists(self, user_id: int):
        result = self.db_conn.execute("""
            select (case when count(*) > 0 then true else false end) as res
            from vkinder_search_conditions
            where 1=1
                and is_open = true
                and id_search_user = %s""", (user_id)).fetchone()
        return result[0]

    def get_state_of_search_user(self, user_id: int):
        result = self.db_conn.execute("""
            select user_state from vkinder_search_user where vk_id = %s""", (user_id)).fetchone()
        return result[0]

    def get_search_conditions(self, user_id: int):
        request = self.db_conn.execute("""
            select
                'city', city,
                'age_from', lower(age_range) as age_from,
                'age_to', upper(age_range) as age_to,
                'sex', sex,
                'relation', relation
            from vkinder_search_conditions
            where 1 = 1
                and is_open = true
                and id_search_user = %s""", (user_id)).fetchone()
        if not request:
            return None
        result = dict()
        result[request[0]] = request[1]
        result[request[2]] = request[3]
        result[request[4]] = request[5]
        result[request[6]] = request[7]
        result[request[8]] = request[9]

        return result

    def _get_current_schema(self):
        return self.db_conn.execute("select current_schema()").fetchall()

    def get_repository_user(self):
        return self.db_conn.execute("select current_user").fetchall()

    def __str__(self):
        return self.connection_string

    def engine_execute(self, SQL, params: dict, exc: Exception, message: str):
        try:
            self.db_engine.execute(SQL, params)
        except Exception as e:
            raise exc(message + str(e))
        return True

    def create_new_search_user(self, user_id: int, user_info: dict):
        SQL = sqlalchemy.text(
            """insert into vkinder_search_user
            (vk_id, first_name, second_name, city, age, sex, relation, user_state)
            values (:vk_id, :first_name, :second_name, :city, :age, :sex, :relation, :user_state)""")
        params = {"vk_id": user_id, "first_name": user_info.get("first_name"),
                  "second_name": user_info.get("last_name"), "city": user_info.get("home_town"),
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

    def get_text_choose_relation(self):
        result = self.db_conn.execute("""
            select relation_id||' - '||relation_nm from spr_relations order by 1""").fetchall()
        return result

    def get_exists_opened_condition(self, user_id: int):
        result = self.db_conn.execute("""
            select id from vkinder_search_conditions
             where id_search_user = %s
                and is_open = true""", (user_id)).fetchone()
        if result:
            return result[0]
        else:
            return None

    def create_new_condition(self, user_id: int):
        SQL = sqlalchemy.text(
            """insert into vkinder_search_conditions
            (id_search_user , city, age_range, sex, relation )
            values (:vk_id, '', '[0,127)', 0, 0)""")
        params = {"vk_id": user_id}
        try:
            # self.db_conn.execute(SQL)
            self.db_engine.execute(SQL, params)
        except Exception as e:
            raise self.VKinderCannotInsert(
                f"Error during insert new search vonditios user with id {user_id} " + str(e))
        return True

    def update_search_condition(self, opened_condition_id: int, search_criteria: str, value: str):
        if search_criteria == "age":
            value = "[" + str(value) + "," + str(value) + "]"
        elif search_criteria == "age_from":
            value = "[" + str(value) + ",127)"
        elif search_criteria == "age_to":
            value = "[0," + str(value) + ")"

        SQL = sqlalchemy.text(
            """update vkinder_search_conditions
                set """ + self.search_fields[search_criteria] + """ = :value
                where id = :opened_condition_id""")
        params = {"value": value, "opened_condition_id": opened_condition_id}
        return self.engine_execute(SQL, params, self.VKinderCannotUpdateSearchConditions,
                                   f"Error during update search condition with id {opened_condition_id} ")

    def add_search_condition(self, user_id: int, search_criteria: str, value: str):
        opened_condition_id = self.get_exists_opened_condition(user_id)
        if not opened_condition_id:
            self.create_new_condition(user_id)
            opened_condition_id = self.get_exists_opened_condition(user_id)
        return self.update_search_condition(opened_condition_id, search_criteria, value)

    def _hard_reset(self):
        self._drop_structure()
        self._create_structure()

    def save_search_result(self, user_id: int, results_to_save: list):
        opened_condition_id = self.get_exists_opened_condition(user_id)

        for item in results_to_save:
            SQL = sqlalchemy.text(
                """INSERT INTO vkinder_searched_pairs
                (
                id_search_condition, id_pair, first_name, second_name, age, sex, city, relation,
                photo1 ,photo2, photo3
                ) VALUES (
                :id_search_condition, :id_pair, :first_name, :second_name, :age, :sex, :city, :relation,
                :photo1 , :photo2, :photo3
                )""")
            params = {"id_search_condition": opened_condition_id, "id_pair": item['id'],
                      "first_name": item.get("first_name"), "second_name": item.get("last_name"),
                      "age": item.get("age"), "sex": item.get("sex"), "city": item.get("city"),
                      "relation": item.get("relation"),
                      "photo1": ('' if item.get("photo1") is None else item.get("photo1")),
                      "photo2": ('' if item.get("photo2") is None else item.get("photo2")),
                      "photo3": ('' if item.get("photo3") is None else item.get("photo3"))
                      }

            self.engine_execute(SQL, params, self.VKinderCannotInsertSearchedResults,
                                f"Error during insert searched results, condition id {opened_condition_id}, " +
                                f"vk_user_id {item['id']}")

        return True

    def get_next_saved_pair(self, user_id: int):
        opened_condition_id = self.get_exists_opened_condition(user_id)

        request = self.db_conn.execute("""
            select
                'saved_pair_id', id,
                'first_name', first_name,
                'second_name', second_name,
                'age', age,
                'sex', sex,
                'city', city,
                'relation', relation,
                'avatar', photo1
            from vkinder_searched_pairs
            where 1 = 1
                and is_offered = false
                and id_search_condition = %s
            order by id asc""", (opened_condition_id)).fetchone()
        if not request:
            return None
        result = dict()
        result[request[0]] = request[1]
        result[request[2]] = request[3]
        result[request[4]] = request[5]
        result[request[6]] = request[7]
        result[request[8]] = request[9]
        result[request[10]] = request[11]
        result[request[12]] = request[13]
        result[request[14]] = request[15]
        return result

    def set_last_pair_to_offered_status(self, user_id):
        opened_condition_id = self.get_exists_opened_condition(user_id)
        pair = self.get_next_saved_pair(user_id)
        if not pair:
            return None
        SQL = sqlalchemy.text(
            """UPDATE vkinder_searched_pairs
            SET is_offered = true
            WHERE 1 = 1
                AND id = :saved_pair_id
            """)
        params = {"saved_pair_id": pair['saved_pair_id']}
        self.engine_execute(SQL, params, self.VKinderCannotUPdateIsOfferedStatusOfPair,
                            f"Error during insert new pair, condition id {opened_condition_id}, " +
                            f"vk_user_id {user_id}, pair_id {pair['saved_pair_id']}")

    def add_pair(self, user_id: int):
        opened_condition_id = self.get_exists_opened_condition(user_id)
        pair = self.get_next_saved_pair(user_id)
        if not pair:
            return None
        SQL = sqlalchemy.text(
            """INSERT INTO vkinder_pair
            (
            id_search_user, id_pair, first_name, second_name, age, sex, city, relation
            )
            SELECT
            :user_id, id_pair, first_name, second_name, age, sex, city, relation
            FROM vkinder_searched_pairs
            WHERE 1 = 1
                AND id = :saved_pair_id""")

        params = {"user_id": user_id, "saved_pair_id": pair['saved_pair_id']}
        self.engine_execute(SQL, params, self.VKinderCannotAddNewPair,
                            f"Error during insert new pair, condition id {opened_condition_id}, " +
                            f"vk_user_id {user_id}, pair_id {pair['saved_pair_id']}")


if __name__ == "__main__":
    repository = Repository(
        'postgresql://vkinder:1@localhost:5432/vkinder', True)
    # print(repository.get_exists_opened_condition(111))
    # print(repository.get_text_choose_sex())
    repository._drop_structure()
    repository._create_structure()
    # print(repository.get_repository_user())
    # print(repository.has_user_exists(4))
