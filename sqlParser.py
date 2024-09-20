import sqlparse
import re
import json
import re
from typing import Dict, List

class RefInfo:
    def __init__(self, foreign_key:str, ref_table:str):
        self.foreign_key = foreign_key
        self.ref_table = ref_table

class TableInfo:
    def __init__(self, name:str):
        self.name = name
        self.primary_key = ''
        self.columns: List[str] = []
        self.uniques: List[str] = []
        self.reference: List[RefInfo] = []

def get_primary_key(column_def: str):
    if 'PRIMARY KEY' not in column_def:
        return None, False

    primary_key_column = re.search(r'PRIMARY\s+KEY\s+\((\w+)\)', column_def)
    if primary_key_column:
        return primary_key_column.group(1), False

    return re.search(r'(\w+)', column_def).group(1), True

def get_unique_key(column_def: str):
    if 'UNIQUE' not in column_def:
        return None, False
    
    unique_key_column = re.search(r'UNIQUE\s+KEY\s+\((\w+)\)', column_def)
    if unique_key_column:
        return unique_key_column.group(1), False
    
    return re.search(r'(\w+)', column_def).group(1), True

def get_reference_table(column_def: str):
    if 'FOREIGN KEY' not in column_def:
        return None, None

    foreign_key_column = re.search(r'FOREIGN\s+KEY\s+\((\w+)\)REFERENCES\s+(\w+)\((\w+)\)', column_def)

    if foreign_key_column:
        return foreign_key_column.group(1), foreign_key_column.group(2)

def get_normal_colname(column_def: str):
    return re.search(r'(\w+)', column_def).group(1)

def parse_sql(sql_statement):
    parsed = sqlparse.parse(sql_statement)

    tbl_to_stmt = {}

    # Init table_infos
    tables: Dict[str, TableInfo] = {}
    for statement in parsed:
        tokens = [t for t in statement.tokens if not t.is_whitespace]
        table_name = str(tokens[2])
        tbl_to_stmt[table_name] = statement
        tables[table_name] = TableInfo(table_name)

    # fill member variables
    for table_name, statement in tbl_to_stmt.items():
        table_info = tables.get(table_name)
        if table_info == None:
            continue

        tokens = [t for t in statement.tokens if not t.is_whitespace]
        for _, token in enumerate(tokens):
            txt = token.value
            if txt.startswith('('):
                columns: List[str] = txt[1 : txt.rfind(')')].replace('\n', '').split(',')
                for column in columns:
                    # case 1: primary key column
                    primary_key, not_constraint = get_primary_key(column)
                    if primary_key:
                        table_info.primary_key = primary_key
                        if not_constraint:
                            table_info.columns.append(primary_key)
                        continue

                    # case 2: unique key column
                    unique_key, not_constraint = get_unique_key(column)
                    if unique_key:
                        table_info.uniques.append(unique_key)
                        if not_constraint:
                            table_info.columns.append(unique_key)
                        continue

                    # case 3: foreign key column
                    foreign_key, ref_table = get_reference_table(column)
                    if foreign_key:
                        table_info.reference.append(
                            RefInfo(foreign_key, ref_table)
                        )
                        continue

                    # case 4: normal column
                    col_name = get_normal_colname(column)
                    if col_name:
                        table_info.columns.append(col_name)
                break

    return tables

def generate_JSON(tables: Dict[str, TableInfo]):
    json_data = []
    for table_name, table_info in tables.items():
        entity_data = {
            'name': table_name,
            'attributes': [],
            'relationships': []
        }

        for column in table_info.columns:
            entity_data['attributes'].append(column)

        for reference in table_info.reference:
            foreign_key = reference.foreign_key
            ref_table = reference.ref_table

            if foreign_key in tables[table_name].uniques:
                entity_data['relationships'].append(
                    {
                        'related_entity': ref_table,
                        'type': 'one_to_one'
                    }
                )
            else:
                entity_data['relationships'].append(
                    {
                        'related_entity': ref_table,
                        'type': 'many_to_one'
                    }
                )
        
        json_data.append(entity_data)

    with open('ERDFromPython.json', 'w+') as file:
        json.dump({'ERD': json_data}, file)