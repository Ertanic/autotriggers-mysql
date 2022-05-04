import os
# from pprint import pprint
from utils.args import get_args
from utils.sql import get_tables_list, prepare_db, generate_queries
import pymysql

args = get_args()
db_name = args.database

connection = pymysql.connect(
    host=args.host, 
    user=args.user, 
    password=args.password,
    cursorclass=pymysql.cursors.DictCursor);

with connection:
    with connection.cursor() as cursor:
        print("1. Получение списка таблиц")
        #   Получение списка таблиц
        table_names = get_tables_list(db_name, cursor)

        print("2. Подготовка таблиц")
        #   Нормализация представления базы данных
        tables = prepare_db(db_name, table_names, cursor)['tables']
        #   Массив для сохранения подзапросов
        queries = []

        print("3. Генерация SQL-запроса")
        #   Объявление об использовании базы данных
        queries.append("USE `{}`;".format(db_name))
        #   Генерация SQL-запросов на создание таблиц и триггеров
        generate_queries(tables, queries)

        #   Путь до файла, в который будет сохранён сгенерированный SQL-запрос
        file_path = os.path.join(os.path.abspath(args.file), 'autotriggers_{}.sql'.format(db_name))
        #   Сборка запроса
        query = "\n".join(queries)

        print("4. Сохранение SQL-запроса в файл по пути: {}", file_path)
        #   Сохранение SQL-запроса в файл
        with open(
            file_path, 
            'w',
            encoding="utf-8") as file:
            file.write(query)

        #   Исполнение сгенерированных запросов
        if not args.without_execute:
            print("5. Исполнение запросов в БД")
            for q in queries:
                cursor.execute(q)

        print("\n✓ Программа успешно выполнена.")