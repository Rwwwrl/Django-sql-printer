from django.conf import settings
from django.db import connection, reset_queries

import sqlparse

DJANGO_DEBUG_SETTING_VALUE = settings.DEBUG


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
  @staticmethod
  def _parse_queries_to_readeble_sql(queryies):
    '''
    распринтить sql-запроса в человеко-читаемом виде
    '''
    print()
    print('НАЧАЛО БЛОКА ----------')
    for query in queryies:
      print()
      sql_string = query['sql']
      parsed_string = sqlparse.format(sql_string, reindent=True, keyword_case='upper')
      print(parsed_string)
      print()
    print('КОНЕЦ БЛОКА ----------')
    print()

  @toggle_debug_mode
  def __enter__(self):
    # очищаем старые запросы
    reset_queries()
    return self

  @toggle_debug_mode
  def __exit__(self, *arsg, **kwargs):
    self._parse_queries_to_readeble_sql(connection.queries)

  def __call__(self, func):
    @toggle_debug_mode
    def call_inner(*args, **kwargs):
      reset_queries()
      func_result = func(*args, **kwargs)
      self._parse_queries_to_readeble_sql(connection.queries)
      return func_result

    return call_inner
