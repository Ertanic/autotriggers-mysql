from typing import Dict, List, Type
from pymysql import cursors
from utils.sql import db_exists
from utils.string_builder import StringBuilder

def create_test_databases(cursor: Type[cursors.Cursor]):
    dbs =  [{
            'db_name': 'one_db',
            'tables': [
                {
                    'table_name': 'good_table',
                    'table_attrs': [
                        {
                            'attr_name': 'good_id',
                            'type': 'int',
                            'isPrimaryKey': True
                        },
                        {
                            'attr_name': 'sometext',
                            'type': 'varchar(50)',
                            'isPrimaryKey': False
                        }
                    ]
                },
                {
                    'table_name': 'lol_table',
                    'table_attrs': [
                        {
                            'attr_name': 'lol_id',
                            'type': 'int',
                            'isPrimaryKey': True
                        },
                        {
                            'attr_name': 'lol_field',
                            'type': 'boolean',
                            'isPrimaryKey': False
                        }
                    ]
                }
            ]
        }, 
        {
            'db_name': 'super_db',
            'tables': [
                {
                    'table_name': 'super_table',
                    'table_attrs': [
                        {
                            'attr_name': 'super_id',
                            'type': 'int',
                            'isPrimaryKey': True
                        },
                        {
                            'attr_name': 'super_text',
                            'type': 'varchar(255)',
                            'isPrimaryKey': False
                        }
                    ]
                }
            ]
        }]
    
    #   Перебор массива баз
    for db in dbs:
        #   Алиас на имя бд
        db_name = db['db_name']

        #   Проверка на существование бд
        if db_exists(cursor, db_name):
            #   Удаление бд, если существует
            cursor.execute("DROP DATABASE `{}`;".format(db_name))
        #   Создание базы
        cursor.execute("CREATE DATABASE `{}`;".format(db_name))
        #   Переключение на контекст созданной базы
        cursor.execute("USE `{}`;".format(db_name))
        
        #   Перебор таблиц базы
        for table in db['tables']:
            #   Алиас на имя таблицы
            table_name = table['table_name']
            #   Удаление таблицы, если та существует
            cursor.execute("DROP TABLE IF EXISTS `{}`;".format(table_name))
            
            table_builder = StringBuilder()
            #   Создание таблицы
            table_builder.Append("CREATE TABLE {} (".format(table_name))
            
            #   Массив для хранения атрибутов таблицы
            attrs_sql = []
            #   Перебор атрибутов таблицы
            for attr in table['table_attrs']:
                #   Сборка атрибута для создания таблицы вида ИМЯ_АТРИБУТА ТИП_ДАННЫХ ПЕРВИЧНЫЙ_КЛЮЧ
                attrs_sql.append("{} {}{}".format(attr['attr_name'], attr['type'], " PRIMARY KEY AUTO_INCREMENT" if attr['isPrimaryKey'] else ""))

            #   Соединение массива атрибутов с разделитем и добавления в строку запроса для создания таблицы
            table_builder.Append("{})".format(", ".join(attrs_sql)))
            #   Выполнение запроса на создание таблицы
            cursor.execute(table_builder.Build())