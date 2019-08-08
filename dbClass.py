class DbWrapper:
    def __init__(self, db_object):
        self.__db = db_object

    def get_data(self, table_name, **kwargs):
        return self.__db.get_data(table_name, **kwargs)

    def insert_data(self, table_name, insertion_data, **kwargs):
        self.__db.insert_data(table_name, insertion_data, **kwargs)

    def get_count(self, table_name):
        return self.__db.get_count(table_name)

    def get_last_insert_id(self):
        return self.__db.get_last_insert_id()

    def execute(self, sql):
        return self.__db.execute_custom_query(sql)
