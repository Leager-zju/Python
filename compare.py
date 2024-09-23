import json
import sqlParser
from typing import Dict, List
from common import TableInfo

def compare_inmemory_data_from_json(path: str, im_tables: Dict[str, TableInfo]):
    with open(path, 'r') as f:
        json_data : List[Dict] = json.load(f).get('ERD')

    for entity in json_data:
        name = entity.get('name')
        primary_key = entity.get('primary_key')
        attributes = entity.get('attributes')
        relationships = entity.get('relationships')

        table_info = im_tables.get(name)
        if table_info == None:
            return False
        
        if primary_key and primary_key != table_info.primary_key:
            return False
        
        for attribute in attributes:
            if attribute not in table_info.columns:
                return False
            
        for relation in relationships:
            foreign_key = relation.get("foreign_key")
            related_entity = relation.get("related_entity")
            type = relation.get("type")

            correct_reference = False
            for ref in table_info.reference:
                if ref.foreign_key != foreign_key:
                    continue

                if ref.ref_table != related_entity:
                    break

                if type == 'one_to_one' and ref.foreign_key not in table_info.uniques:
                    break

                correct_reference = True
            
            if not correct_reference:
                return False
        
    return True

with open("test1.sql", "r", encoding="utf8") as sql_file:
    table_info = sqlParser.parse_sql(sql_file.read().strip())

if compare_inmemory_data_from_json('ERDFromChat.json', table_info):
    print('Success')
else:
    print('Fail')