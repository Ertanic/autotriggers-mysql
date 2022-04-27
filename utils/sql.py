from ast import Tuple
from typing import Dict, List, Type
from pymysql import cursors

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
                'field_name': f['Field'],
                'type': f['Type'],
                'isPrimaryKey': f['Key'] == 'PRI'
            },
            data
        )
    )

def prepare_tables(db_name: str, table_names: List[str], cursor: Type[cursors.Cursor]) -> Dict[str, List[Dict[str, List[Dict]]]]:
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