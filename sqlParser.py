import sqlparse
import re
import json
import re
from typing import Dict, List
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
    def __init__(self, entityA:str, entityB:str, relation_type:RelationType = RelationType.NONE) -> None:
        self.A = entityA
        self.B = entityB
        self.type = relation_type

class JsonData:
    def __init__(self) -> None:
        self.entities: List[MetaData] = []
        self.relationships: List[Relation] = []



def get_primary_key(column_def: str):
    if 'PRIMARY KEY' not in column_def:
        return None, False

    primary_key_column = re.search(r'PRIMARY\s+KEY\s+\((\w+)\)', column_def)

    if primary_key_column:
        return primary_key_column.group(1), False

    return re.search(r'(\w+)', column_def).group(1), True

def get_unique_key(column_def: str):
    if 'UNIQUE' not in column_def:
        return None
    
    unique_key_column = re.search(r'UNIQUE\s+\((\w+)\)', column_def)
    if unique_key_column:
        return unique_key_column.group(1)
    
    return re.search(r'(\w+)', column_def).group(1)

def get_reference_table(column_def: str):
    if 'FOREIGN KEY' not in column_def:
        return None, None

    foreign_key_column = re.search(r'REFERENCES\s+(\w+)\((\w+)\)', column_def)

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
                    unique_key = get_unique_key(column)
                    if unique_key:
                        table_info.uniques.append(unique_key)
                        table_info.columns.append(unique_key)
                        continue

                    # case 3: foreign key column
                    ref_table, ref_key = get_reference_table(column)
                    if ref_table:
                        table_info.reference.append(
                            RefInfo(ref_table, ref_key)
                        )
                        continue

                    # case 4: normal column
                    col_name = get_normal_colname(column)
                    if col_name:
                        table_info.columns.append(col_name)
                break

    return tables

def generate_JSON(tables: Dict[str, TableInfo]):
    json_data = {
        'entities': [],
        'relationships': []
    }

    for table_name, table_info in tables.items():
        entity_data = {
            'name': table_name,
            'attributes': [],
        }

        for column in table_info.columns:
            entity_data['attributes'].append(column)

        for i in range(len(table_info.reference)):
            referenceA = table_info.reference[i]
            ref_table_A = referenceA.ref_table
            ref_key_A = referenceA.ref_key

            if ref_key_A in tables[ref_table_A].uniques:
                json_data['relationships'].append(
                    {
                        'lhs': ref_table_A,
                        'rhs': table_name,
                        'type': 'one_to_one'
                    }
                )
            else:
                json_data['relationships'].append(
                    {
                        'lhs': ref_table_A,
                        'rhs': table_name,
                        'type': 'one_to_many'
                    }
                )
            
                for j in range(i+1, len(table_info.reference)):
                    referenceB = table_info.reference[j]
                    ref_table_B = referenceB.ref_table
                    ref_key_B = referenceB.ref_key

                    if ref_key_B == tables[ref_table_B].primary_key:
                        json_data['relationships'].append(
                            {
                                'lhs': ref_table_A,
                                'rhs': ref_table_B,
                                'type': 'many_to_many'
                            }
                        )
        
        json_data['entities'].append(entity_data)

    with open('ERDFromPython.json', 'w+') as file:
        json.dump({'ERD': json_data}, file)