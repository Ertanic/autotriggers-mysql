import argparse

def get_args():
    args_parser = argparse.ArgumentParser(description="В автоматическом режиме создаёт таблицы и триггеры для существующих таблиц в указанной БД")
    args_parser.add_argument('--host', 
        type=str, 
        default="localhost",
        help="Указывает хост MySQL-сервера")
    args_parser.add_argument('-u', '--user',
        type=str,
        default="root",
        help="Указывает имя пользователя MySQL")
    args_parser.add_argument('-p', '--password',
        type=str,
        default='',
        help="Указывает пароль к пользователю MySQL")
    args_parser.add_argument('-db', '--database',
        type=str,
        required=True,
        help="Указывает имя базы данных, для которой необходимо произвести создание триггеров")
    args_parser.add_argument('--auto', '--auto_create',
        action="store_true",
        help="При указании данного параметра будет произведена генерация триггеров и необходимых таблиц в автоматическом режиме без импорта в файл")
    args_parser.add_argument('-f', '--file',
        default='./',
        type=str,
        help="Принимает путь, по которому будет сгенерирован .sql-файл с запросами, если параметр --auto_create не указан")
    args_parser.add_argument('--test_database',
        action="store_true")

    return args_parser.parse_args()