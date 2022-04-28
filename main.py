import os
from pprint import pprint
from utils.args import get_args
from utils import sql
from utils.string_builder import StringBuilder
from utils.test_db import create_test_databases
import pymysql

args = get_args()
db_name = args.database

connection = pymysql.connect(
    host=args.host, 
    user=args.user, 
    password=args.password,
    cursorclass=pymysql.cursors.DictCursor);

#   TODO: Вынести в отдельный файл(ы)
with connection:
    with connection.cursor() as cursor:
        if args.test_database:
            create_test_databases(cursor)

        table_names = sql.get_tables_list(db_name, cursor)

        #   Нормализация представления базы данных
        tables = sql.prepare_db(db_name, table_names, cursor)['tables']
        pprint(tables)
        queries = []
        trigger_types = [
            {
                'type': 'INSERT',
                'message_log': "Добавлена запись",
                'time': 'AFTER'
            },
            {
                'type': 'UPDATE',
                'message_log': "Запись обновлена",
                'time': 'BEFORE'
            },
            {
                'type': 'DELETE',
                'message_log': "Запись удалена",
                'time': 'BEFORE'
            }
        ]

        queries.append("USE `{}`;".format(db_name))
        for table in tables:
            queries.append("/* Работа с таблицей {} */".format(table['table_name']))
            queries.append("/* Удаление таблиц логирования и резервного копирования для таблицы {} */".format(table['table_name']))
            queries.append("DROP TABLE IF EXISTS `Logs_{}`;".format(table['table_name']))
            queries.append("DROP TABLE IF EXISTS `Backups_{}`;".format(table['table_name']))

            queries.append("/* Удаление триггеров для таблицы {} */".format(table['table_name']))
            for trigger in trigger_types:
                queries.append("DROP TRIGGER IF EXISTS `{}_{}_tr`;".format(table['table_name'], trigger['type'].lower(),))
            

            queries.append("/* Создание таблицы для логирования действий в таблице {} */".format(table['table_name']))

            #   Проверяем наличие первичного ключа в таблице
            try:
                primary_key = list(filter(lambda attr: attr['isPrimaryKey'], table['attrs']))[0]
            except Exception:
                raise Exception("Не найден первичный ключ в таблице {}".format(table['table_name']))

            #   Генерация таблицы логов
            queries.append(
"""CREATE TABLE `Logs_{}` (
    `LogsID_{}` int NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `LogsDate` date NOT NULL,
    `LogsTime` time NOT NULL,
    `LogsUser` varchar(255) NOT NULL,
    `LogsMessage` varchar(255) NOT NULL,
    `Logs_{} {} NOT NULL`
);""".format(table['table_name'], table['table_name'], primary_key['attr_name'], primary_key['type']))
            
            #   Генерация таблиц бэкапов
            queries.append("/* Создание таблицы для резервного копирования данных из таблицы {} */".format(table['table_name']))
            backup_attrs_sql = []   # Массив для хранения сформированных атрибутов таблицы
            for attr in table['attrs']:
                backup_attrs_sql.append("`Backup_{}` {}{}".format(attr['attr_name'], attr['type'], " PRIMARY KEY AUTO_INCREMENT" if attr['isPrimaryKey'] else ""))
            #   Формирование запроса на создание таблицы
            queries.append("CREATE TABLE `Backups_{}` (\n    `BackupID_{}` int NOT NULL PRIMARY KEY AUTO_INCREMENT,\n    {}\n);".format(
                table['table_name'],
                table['table_name'],
                ",\n    ".join(backup_attrs_sql)))

            #   Создание триггеров для логирования
            queries.append("/* Создание триггеров для таблицы {} */".format(table['table_name']))
            #   Получение форматированных атрибутов для триггера
            trigger_attrs_sql = []
            for attr in table['attrs']:
                trigger_attrs_sql.append("`Backups_{0}`.`Backup_{1}` = OLD.`{1}`".format(table['table_name'], attr['attr_name']))

            for trigger in trigger_types:
                queries.append(
"""DELIMITER ;
CREATE TRIGGER `{0}_{1}_tr` {2} {3} ON `{0}`
FOR EACH ROW
BEGIN
    INSERT `{5}` SET
    `{5}`.`LogsDate` = CURRENT_DATE,
    `{5}`.`LogsTime` = CURRENT_TIME,
    `{5}`.`LogsUser` = CURRENT_USER,
    `{5}`.`LogsMessage` = `{6}`
    `{5}`.`Logs_{4}` = NEW.`{4}`;{7}
END;
""".format(table['table_name'], 
    trigger['type'].lower(), 
    trigger['time'], 
    trigger['type'], 
    primary_key['attr_name'], 
    'Logs_{}'.format(table['table_name']), 
    trigger['message_log'],
"""\n    INSER `Backups_{}` SET
    {};""".format(table['table_name'], ",\n    ".join(trigger_attrs_sql)) if not (trigger['type'] == "INSERT") else "" ))

        print('\n'.join(queries))

        # TODO: Реализовать и автоматический режим
        # if args.auto:
        #     ()
        # else:
        with open(
            os.path.join(
                os.path.abspath(args.file), 
                'autotriggers_{}.sql'.format(db_name)), 
            'w',
            encoding="utf-8") as file:
            file.write("\n".join(queries))