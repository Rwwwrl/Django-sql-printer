from django.conf import settings
from django.db import connections, reset_queries
from django.db.utils import DEFAULT_DB_ALIAS

import time

import sqlparse

DJANGO_DEBUG_SETTING_VALUE = settings.DEBUG


def create_filename():
    filename = f'sql_log_{str(int(time.time()))[5:]}'
    return f'{filename}.sql'


def toggle_debug_mode(func):
    '''
    декоратор для включения режима DEBUG = True в тестах
    '''
    def inner(*args, **kwargs):
        settings.DEBUG = True
        func_result = func(*args, **kwargs)
        if not func.__name__ == '__enter__':
            settings.DEBUG = DJANGO_DEBUG_SETTING_VALUE
        return func_result

    return inner


class PrintSqlTool:
    '''
    класс главной задачей, которого является принт sql запросов
    '''
    def __init__(self, db_alias: str = DEFAULT_DB_ALIAS, write_to_file: bool = False, disable: bool = False):
        '''
        @params db_alias - алиас бд в джанго проекте, пример "default" 
        @params write_to_file - если True, то sql будет записываться в файл, а не выводиться в консоль
        @params disable - если True, то никакой логики запущено не будет. Это удобно, чтобы не комментировать код,
         а просто его выключить и обратно к нему вернуться, когда такая возможность потребуется
        '''
        self.connection = connections[db_alias]
        self._write_to_file = write_to_file
        self._is_disabled = disable

    def _parse_queries_to_readeble_sql(self, queryies) -> list:
        '''
        распринтить sql-запроса в человеко-читаемом виде
        '''
        result = []
        for query in queryies:
            sql_string = query['sql']
            parsed_string = sqlparse.format(sql_string, reindent=True, keyword_case='upper')
            result.append(parsed_string)
        return result

    def _write_or_print_parsed_quaries(self, parsed_quaries: list) -> None:
        if not self._write_to_file:
            print()
            print('НАЧАЛО БЛОКА ----------')
            for q in parsed_quaries:
                print()
                print(q)
                print()
            print('КОНЕЦ БЛОКА ----------')
            print()
        else:
            body = ''
            body += '-- Начало запроса\n'
            for q in parsed_quaries:
                body += q + '\n'
            body += '-- Конец запроса'
            with open(create_filename(), 'w') as file:
                file.write(body)

    @toggle_debug_mode
    def __enter__(self):
        # очищаем старые запросы
        if self._is_disabled:
            return self
        reset_queries()
        return self

    @toggle_debug_mode
    def __exit__(self, exc_type, *args):
        if exc_type:
            return

        if self._is_disabled:
            return
        parsed_quaries = self._parse_queries_to_readeble_sql(self.connection.queries)
        self._write_or_print_parsed_quaries(parsed_quaries=parsed_quaries)
        return True

    def __call__(self, func):
        @toggle_debug_mode
        def call_inner(*args, **kwargs):
            reset_queries()
            func_result = func(*args, **kwargs)
            self._parse_queries_to_readeble_sql(self.connection.queries)
            return func_result

        return call_inner
