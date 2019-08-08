import pymysql.cursors
import pymysql
import json


class DbMysql:

    def __init__(self, host, port, user, password, db):
        """
        :param host: Host address or IP of the machine that mysql runs on
        :param user: Username for mysql connection
        :param password: Password for mysql connection
        :param db: Database that is going to be used
        """
        self._connection = pymysql.connect(host=host,
                                           port=port,
                                           user=user,
                                           password=password,
                                           db=db,
                                           charset='utf8mb4',
                                           cursorclass=pymysql.cursors.DictCursor)

    @staticmethod
    def __build_get_query(table_name, **kwargs):
        """
        Builds a select query with given arguments and returns it
        :param table_name: Name of the target table
        :param kwargs: Arguments that contain clauses and wished columns to build query
        :return: Returns the sql which is built by the function
        """
        sql = "SELECT {COLUMN_NAME} FROM {TABLE_NAME}"
        cmp = '=' if kwargs['OPERATOR'] == 'eq' else '>' if kwargs['OPERATOR'] == 'g' else '='
        for key, value in kwargs.items():
            if key.lower() == 'columns':
                columns = ','.join([column for column in value]).rstrip(',')
                sql = sql.format(COLUMN_NAME=columns, TABLE_NAME=table_name)

            elif key.lower() == 'where':
                for clause in value:
                    cl = list(clause.keys())[0]
                    clause_key = list(clause[cl].keys())[0]

                    if cl == 'init':
                        clause_value = clause[cl][clause_key]
                        sql += " WHERE {CONDITION}{OPERATOR}'{VALUE}'".format(CONDITION=clause_key, VALUE=clause_value,
                                                                              OPERATOR=cmp)

                    elif cl == 'or':
                        clause_value = clause[cl][clause_key]
                        sql += " or {CONDITION}='{OPERATOR}'".format(CONDITION=clause_key, VALUE=clause_value,
                                                                     OPERATOR=cmp)

                    elif cl == 'and':
                        clause_value = clause[cl][clause_key]
                        sql += " and {CONDITION}{OPERATOR}'{VALUE}'".format(CONDITION=clause_key, VALUE=clause_value,
                                                                            OPERATOR=cmp)
        return sql + (' LIMIT {0}'.format(str(kwargs['LIMIT'])) if 'LIMIT' in kwargs else '')

    @staticmethod
    def __build_insert_query(table_name, data_len, **kwargs):
        """
        Builds an insert query with given arguments and returns it
        :param table_name: Name of the target table
        :param kwargs: Arguments that contain clauses and wished columns to build query
        :return: Returns the sql which is built by the function
        """
        sql = "INSERT INTO {TABLE_NAME}({COLUMN_NAMES}) VALUES("
        column_names = ','.join(
            [column for key, value in kwargs.items() for column in value if key.lower() == 'columns'])
        sql = sql.format(TABLE_NAME=table_name, COLUMN_NAMES=column_names)
        sql += ','.join(['%s' for _ in (range(data_len))]).strip(' ') + ')'
        return sql

    def get_data(self, table_name, **kwargs):
        """
        Builds the query by given arguments and executes it to get data and then returns it
        :param table_name: Name of the target table
        :param kwargs: Arguments that contain clauses and wished columns to build query
        :return: Returns the data
        """
        with self._connection.cursor() as cursor:
            sql = self.__build_get_query(table_name, **kwargs)
            cursor.execute(sql)
            result = cursor.fetchall()
            return result

    def insert_data(self, table_name, insertion_data, **kwargs):
        """
        :param table_name: Name of the target table
        :param insertion_data: The data which will be inserted. Data should be a list which contains tuples as rows
        :param kwargs: Arguments that contain clauses and wished columns to build query
        :return:
        """
        with self._connection.cursor() as cursor:
            sql = self.__build_insert_query(table_name, len(insertion_data[0]), **kwargs)
            cursor.executemany(sql, insertion_data)
            self._connection.commit()

    def get_count(self, table_name):
        with self._connection.cursor() as cursor:
            sql = 'SELECT count(*) from {0}'.format(table_name)
            cursor.execute(sql)
            result = cursor.fetchone()['count(*)']
            return result

    def get_last_insert_id(self):
        with self._connection.cursor() as cursor:
            cursor.execute('SELECT last_insert_id()')
            result = cursor.fetchone()['last_insert_id()']
            return result

    def update_data(self, table_name, update_data, row_id):
        with self._connection.cursor() as cursor:
            # UPDATE table SET last_update=now(), last_monitor=last_update WHERE id=1;
            update_string, sql = "", ""
            update_list = []
            print(update_data)
            for (key, value) in update_data:
                update_list.append(key + '="' + value + '"')
            update_string = ','.join(update_list)

            if update_string != "":
                sql = 'UPDATE ' + table_name + ' SET ' + update_string + ' WHERE id=' + str(row_id) + ';'
            print(sql)
            cursor.execute(sql)
            self._connection.commit()
            result = cursor.fetchall()
            return result

    def execute_custom_query(self, sql):
        with self._connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
