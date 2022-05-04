import re
from typing import Dict, List, Type
from pymysql import cursors
from utils.structurs.trigger_types import trigger_types

def generate_queries(tables: List, queries: List):
    tables = list(filter(lambda t: re.match(r'(backups|logs)_+', t['table_name']) == None, tables))

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
`Logs_{}` {} NOT NULL
);""".format(table['table_name'], table['table_name'], primary_key['attr_name'], primary_key['type']))
        
        #   Генерация таблиц бэкапов
        queries.append("/* Создание таблицы для резервного копирования данных из таблицы {} */".format(table['table_name']))
        backup_attrs_sql = []   # Массив для хранения сформированных атрибутов таблицы
        for attr in table['attrs']:
            backup_attrs_sql.append("`Backup_{}` {}".format(attr['attr_name'], attr['type']))
        #   Формирование запроса на создание таблицы
        queries.append("CREATE TABLE `Backups_{0}` (\n    `BackupID_{0}` int NOT NULL PRIMARY KEY AUTO_INCREMENT,\n    {1}\n);".format(
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
"""DELIMITER |
CREATE TRIGGER `{0}_{1}_tr` {2} {3} ON `{0}`
FOR EACH ROW
BEGIN
    INSERT `{5}` SET
    `{5}`.`LogsDate` = CURRENT_DATE,
    `{5}`.`LogsTime` = CURRENT_TIME,
    `{5}`.`LogsUser` = CURRENT_USER,
    `{5}`.`LogsMessage` = "{6}",
    `{5}`.`Logs_{4}` = {8}.`{4}`;{7}
END;""".format(table['table_name'], 
    trigger['type'].lower(), 
    trigger['time'], 
    trigger['type'], 
    primary_key['attr_name'], 
    'Logs_{}'.format(table['table_name']), 
    trigger['message_log'],
"""\n    INSER `Backups_{}` SET
    {};""".format(table['table_name'], ",\n    ".join(trigger_attrs_sql)) if not (trigger['type'] == "INSERT") else "",
    "OLD" if trigger['time'] == "BEFORE" else "NEW"))

    return queries

def get_tables_list(db_name: str, cursor: Type[cursors.Cursor]) -> List[str]:
    sql = 'SHOW TABLES FROM {}'.format(db_name)

    cursor.execute(sql)
    data = cursor.fetchall()

    return list(
            map(
                lambda e: e['Tables_in_{}'.format(db_name)], 
                data
            )
        )

def get_attributes(table_name: str, db_name: str, cursor: Type[cursors.Cursor]) -> List[Dict]:
    sql = 'SHOW COLUMNS FROM {} FROM {};'.format(table_name, db_name)
    
    cursor.execute(sql)
    data = cursor.fetchall()
    
    return list(
        map(
            lambda f: {
                'attr_name': f['Field'],
                'type': f['Type'] if not (f['Type'] == "int(11)") else "int",
                'isPrimaryKey': f['Key'] == 'PRI'
            },
            data
        )
    )

def prepare_db(db_name: str, table_names: List[str], cursor: Type[cursors.Cursor]) -> Dict[str, List[Dict[str, List[Dict]]]]:
    prepared_tables = {
        'db_name': db_name,
        'tables': []
    }
    for t_name in table_names:
        table_attrs = get_attributes(t_name, db_name, cursor)

        prepared_tables['tables'].append({
            'table_name': t_name,
            'attrs': table_attrs,
        })
    
    return prepared_tables