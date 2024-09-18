import sqlparse
import re
import xml.etree.ElementTree as ET
import xml.dom.minidom as md

def parse_sql(sql_statement):
    parsed = sqlparse.parse(sql_statement)
    tables = {}

    for statement in parsed:
        tokens = [t for t in statement.tokens if not t.is_whitespace]
        table_name = str(tokens[2])
        table_info = {}
        table_info["columns"] = []
        table_info["reference"] = []
        for _, token in enumerate(tokens):
            if token.value.startswith("("):
                txt = token.value
                columns = txt[1 : txt.rfind(")")].replace("\n", "").split(",")
                for column in columns:
                    c = " ".join(column.split()).split()

                    c_name = c[0].replace('"', "")

                    if c_name.upper() == "PRIMARY":
                        table_info["primary_key"] = c[2].strip("()")
                    elif c_name.upper() == "FOREIGN":
                        matches = re.match(r"(\w+)\((\w+)\)", c[4])
                        foreign_key_info = {
                            "columns": c[2].strip("()"),
                            "references_table": matches.group(1),
                            "references_columns": matches.group(2),
                        }
                        table_info["reference"].append(foreign_key_info)
                    else:
                        table_info["columns"].append(c_name)
                break
        tables[table_name] = table_info
    return tables


def generate_er_xml(table_info: dict):
    er_model = ET.Element("ERModel")
    for table_name, table in table_info.items():
        entity = ET.SubElement(er_model, "entity", {"name": table_name})
        for column in table["columns"]:
            attribute = ET.SubElement(entity, "attribute", {"name": column})
            if column == table.get("primary_key"):
                ET.SubElement(attribute, "primaryKey")
        for reference in table.get("reference"):
            relationship_element = ET.SubElement(
                er_model, "relationship", {"type": "one-to-many"}
            )
            ET.SubElement(relationship_element, "entity", {"from": table_name})
            ET.SubElement(
                relationship_element, "entity", {"to": reference["references_table"]}
            )

    tree = ET.ElementTree(er_model)
    rawText = ET.tostring(tree.getroot())
    dom = md.parseString(rawText)
    with open("er_model.xml", "w") as f:
        dom.writexml(f, "", "\t", "\n", "utf-8")