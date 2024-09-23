from typing import List

class RefInfo:
    def __init__(self, foreign_key:str = '', ref_table:str = ''):
        self.foreign_key = foreign_key
        self.ref_table = ref_table
    
    def __repr__(self) -> str:
        return f"RefInfo(foreign_key={self.foreign_key}, ref_table={self.ref_table})"

class TableInfo:
    def __init__(self, name:str):
        self.name = name
        self.primary_key = ''
        self.columns: List[str] = []
        self.uniques: List[str] = []
        self.reference: List[RefInfo] = []

    def __repr__(self) -> str:
        return f"TableInfo(name={self.name}, primary_key={self.primary_key}, columns={self.columns}, uniques={self.uniques}, reference={self.reference})"