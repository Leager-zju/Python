import sqlparse
import re
import json
import re
from typing import Dict, List, Optional
from enum import Enum

class RefInfo:
    def __init__(self, ref_table:str, ref_key:str):
        self.ref_table = ref_table
        self.ref_key = ref_key

class TableInfo:
    def __init__(self, name:str):
        self.name = name
        self.primary_key = ''
        self.columns: List[str] = []
        self.uniques: List[str] = []
        self.reference: List[RefInfo] = []

class RelationType(Enum):
    NONE = 0
    ONE_TO_ONE = 1
    ONE_TO_MANY = 2
    MANY_TO_MANY = 3

class MetaData:
    def __init__(self, entity_name:str):
        self.entity = entity_name
        self.attributes: List[str] = []

class Relation:
    def __init__(self, entityA:str, entityB:str) -> None:
        self.A = entityA
        self.B = entityB
        self.type = RelationType.NONE

class JsonData:
    def __init__(self) -> None:
        self.entities: List[MetaData] = []
        self.relationships: List[Relation] = []



def get_primary_key(column_def: str):
    if 'PRIMARY KEY' not in column_def:
        return None

    primary_key_column = re.search(r'PRIMARY\s+KEY\s+\((\w+)\)', column_def)

    if primary_key_column:
        return primary_key_column.group(1)

    primary_key = re.search(r'(\w+)', column_def).group(1)
    return primary_key

def get_unique_key(column_def: str):
    if 'UNIQUE' not in column_def:
        return None
    
    unique_key_column = re.search(r'UNIQUE\s+\((\w+)\)', column_def)
    if unique_key_column:
        return unique_key_column.group(1)
    
    unique_key = re.search(r'(\w+)', column_def).group(1)
    return unique_key

def get_reference_table(column_def: str):
    if 'FOREIGN KEY' not in column_def:
        return None, None

    foreign_key_column = re.search(r'REFERENCES (\w+)\((\w+)\)', column_def)

    if foreign_key_column:
        return foreign_key_column.group(1), foreign_key_column.group(2)

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
                columns = txt[1 : txt.rfind(')')].replace('\n', '').split(',')
                for column in columns:
                    # case 1: primary key column
                    primary_key = get_primary_key(column)
                    if primary_key:
                        table_info.primary_key = primary_key
                        continue

                    # case 2: unique key column
                    unique_key = get_unique_key(column)
                    if unique_key:
                        table_info.uniques.append(unique_key)
                        continue

                    # case 3: foreign key column
                    ref_table, ref_key = get_reference_table(column)
                    if ref_table:
                        table_info.reference.append(
                            RefInfo(ref_table, ref_key)
                        )
                        continue

                    # case 4: normal column
                    col_name = re.match(r'\b(\w+)\b', column)
                    table_info.columns.append(col_name.group(1))
                break
    return tables

def generate_JSON(tables: Dict[str, TableInfo]):
    data_list : List[MetaData] = []
    for table_name, table_info in tables.items():
        data = MetaData(table_name)

        for column in table_info.columns:
            data.attributes.append(column)

        for reference in table_info.reference:
            ref_table = reference.ref_table
            ref_key = reference.ref_key

            relationship = Relation(ref_table, table_name)
            if ref_key in tables[ref_table].uniques:
                relationship.type = RelationType.ONE_TO_ONE
            

            data.relationships.append(relationship)
        
        data_list.append(data)
    
    json_data = json.dump({'ERD': data_list})
    with open('ERDFromPython.json', 'w+') as file:
        file.write(json_data)