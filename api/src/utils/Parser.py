from ply import yacc
from utils.Lexer import SQLLexer
from os import path
from os.path import realpath
from pandas import DataFrame
import pandas as pd
import re

TABLES_PATH = realpath(__file__).replace("\\", "/").replace("src/utils/Parser.py", "data/").lower()

class SQLParser:
    
    tokens = SQLLexer.tokens
    update_identifiers = []
    
    def __init__(self):
        
        df = pd.read_csv(TABLES_PATH + "tables.csv")
        self.tables = dict(zip(df['id'], df['csv_name']))
        self.error_status = False
        self.error_message = ""
        self.query_result = None
        self.lexer = SQLLexer()
        self.parser = yacc.yacc(module=self)
    
    def remove_items(self, test_list, item): 
        res = list(filter((item).__ne__, test_list)) 
        return res 

    def do_columns_exist(self, table: DataFrame, columns: list[str]):
        for column in columns:
            if column not in table:
                return False, column
        return True, None

    def do_table_exist(self, table_name: str):
        if table_name in self.tables.keys():
            return True
        return False
    
    def clean_fields(self, fields):
        cleaned_fields: list[str] = []
        for field in fields:
            try:
                if(float(field) == int(float(field))):
                    cleaned_fields.append(int(float(field)))
                else:
                    cleaned_fields.append(float(field))
            except ValueError:
                cleaned_fields.append(field.strip().replace("'", ""))
        return cleaned_fields
    
    def clean_columns_from_string(self, conditions: str):
        
        columns = re.findall(r"[A-Za-z]+", conditions.replace(" and ", "").replace(" or ", ""))
        strings: list[str] = re.findall(r"'[A-Za-z]+|[A-Za-z]+'", conditions)
        
        cleaned_strings = []
        for string in strings:
            cleaned_strings.append(string.replace("'", "").strip())
            
        if(len(strings) <= 0):
            return columns
        
        cleaned_columns = columns
        for clean_string in cleaned_strings:
            cleaned_columns = self.remove_items(cleaned_columns, clean_string)
        
        return cleaned_columns
        
    def p_statement(self, p: list[str]):
        'statement : query SEMICOLON'

    def p_query(self, p: list[str]):
        '''query : selection
                 | deletion
                 | insertion
                 | updation
                 | showing'''
        self.query_result = f"{p[1]}"

    def p_show_tables(self, p: list[str]):
        '''showing : SHOW TABLES'''
        tables = self.tables.keys()
        output = ""
        
        for table in tables:
            output += f"{table}\n"
            
        p[0] = output
        
        
    
    def p_set_table_from(self, p: list[str]):
        'setting : SET TABLE STRING AS IDENTIFIER'
        file_path = p[3][1:-1]

        if not (path.exists(file_path) and path.isfile(file_path)):
            self.error_status = True
            self.error_message = f"<<! ERROR: Can't find file at '{file_path}'"
            return

        self.tables.update({p[5].lower(): file_path})
        p[0] = f"Table '{p[5]}' set from file '{file_path}'."

    def p_select_from_table(self, p: list[str]):
        'selection : SELECT columns FROM table'
        
        if not self.do_table_exist(p[4]):
            self.error_status = True
            p[0] = f"ERROR: La tabla {p[4]} no existe"
            return p[0]
        
        columns = p[2].replace(" ", "").split(",")
        table = pd.read_csv(TABLES_PATH + self.tables[p[4]])
        
        if(p[2].strip() != "*"):
            columns_exist, column = self.do_columns_exist(table, columns)
            if not columns_exist:
                self.error_status = True
                p[0] = f"ERROR: La columna {column} no existe en {p[4]}"
                return p[0]
            p[0] = table[columns].to_string(index=False)
        else:
            p[0] = table.to_string(index=False)
            
        return p[0]
        
    def p_select_from_expression(self, p: list[str]):
        'selection : SELECT columns FROM table WHERE expression'
        
        if not self.do_table_exist(p[4]):
            self.error_status = True
            p[0] = f"ERROR: La tabla {p[4]} no existe"
            return p[0]
        
        columns = p[2].replace(" ", "").split(",")
        table = pd.read_csv(TABLES_PATH + self.tables[p[4]])
        
        if(p[2].strip() != "*"):
            
            columns_exist, column = self.do_columns_exist(table, columns)
            if not columns_exist:
                self.error_status = True
                p[0] = f"ERROR: La columna {column} no existe en {p[4]}"
                return p[0]
            
            table = table[columns]
        
        conditions = p[6].strip().replace(" and ", " & ").replace(" or ", " | ").replace("=", "==")
        filtered_table = table.query(conditions)
        
        p[0] = filtered_table.to_string(index=False)

    def p_delete_from(self, p: list[str]):
        'deletion : DELETE FROM table'
        
        if not self.do_table_exist(p[3]):
            self.error_status = True
            p[0] = f"ERROR: La tabla {p[3]} no existe"
            return p[0]
        
        table = pd.read_csv(TABLES_PATH + self.tables[p[3]])
        table = table[0:0]
        table.to_csv(TABLES_PATH + self.tables[p[3]], index=False)
        
        p[0] = f"Todas las filas borradas de {p[3]}."

    def p_delete_from_where(self, p: list[str]):
        'deletion : DELETE FROM table WHERE expression'
        
        if not self.do_table_exist(p[3]):
            self.error_status = True
            p[0] = f"ERROR: La tabla {p[3]} no existe"
            return p[0]
        
        table = pd.read_csv(TABLES_PATH + self.tables[p[3]])
        
        conditions = p[5].strip().replace(" and ", " & ").replace(" or ", " | ").replace("=", "==")
        columns = self.clean_columns_from_string(conditions)
            
        columns_exist, column = self.do_columns_exist(table, columns)
        if not columns_exist:
            self.error_status = True
            p[0] = f"ERROR: La columna {column} no existe en {p[3]}"
            return p[0]
    
        filtered_table = table.query(conditions)
        
        mask = table.isin(filtered_table.to_dict(orient='list')).all(axis=1)
        table = table[~mask]
        
        table.to_csv(TABLES_PATH + self.tables[p[3]], index=False)
        
        p[0] = f"Filas borrdas de la tabla {p[3]} con la condicion {p[5]}."

    def p_insert_into_table_fields(self, p: list[str]):
        'insertion : INSERT INTO table VALUES LPAREN fields RPAREN'
        
        if not self.do_table_exist(p[3]):
            self.error_status = True
            p[0] = f"ERROR: La tabla {p[3]} no existe"
            return p[0]
        
        table = pd.read_csv(TABLES_PATH + self.tables[p[3]])
        fields = p[6].split(",")
        
        cleaned_fields = self.clean_fields(fields)
        
        table.loc[len(table)] = cleaned_fields
        table.to_csv(TABLES_PATH + self.tables[p[3]], index=False)
        
        p[0] = f"Valores {cleaned_fields} insertados en la tabla {p[3]}."  

    def p_insert_into_table_columns_fields(self, p: list[str]):
        'insertion : INSERT INTO table LPAREN columns RPAREN VALUES LPAREN fields RPAREN'
        
        if not self.do_table_exist(p[3]):
            self.error_status = True
            p[0] = f"ERROR: La tabla {p[3]} no existe"
            return p[0]
        
        columns = p[5].replace(" ", "").split(",")
        table = pd.read_csv(TABLES_PATH + self.tables[p[3]])
        fields = p[9].split(",")
        
        columns_exist, column = self.do_columns_exist(table, columns)
        if not columns_exist:
                self.error_status = True
                p[0] = f"ERROR: La columna {column} no existe en {p[3]}"
                return p[0]
        
        cleaned_fields = self.clean_fields(fields)
        
        if len(cleaned_fields) > len(columns):
            self.error_status = True
            p[0] = f"ERROR: Valores fuera de rango de columnas"
            return p[0]
        
        while(len(cleaned_fields) < len(table.columns)):
            cleaned_fields.append("")
        
        table.loc[len(table)] = cleaned_fields
        table.to_csv(TABLES_PATH + self.tables[p[3]], index=False)
        
        p[0] = f"Valores {cleaned_fields} insertados en las columnas {columns} de la tabla {p[3]}."

    def p_update_set_where(self, p: list[str]):
        'updation : UPDATE table SET updates WHERE expression'
        
        if not self.do_table_exist(p[2]):
            self.error_status = True
            p[0] = f"ERROR: La tabla {p[2]} no existe"
            return p[0]
        
        table = pd.read_csv(TABLES_PATH + self.tables[p[2]])
        
        update_columns = self.clean_columns_from_string(p[4])
        columns_exist, found_column = self.do_columns_exist(table, update_columns)
        if not columns_exist:
                self.error_status = True
                p[0] = f"ERROR: La columna {found_column} no existe en {p[3]}"
                return p[0]
            
        conditions_columns = self.clean_columns_from_string(p[6])
        columns_exist, found_column = self.do_columns_exist(table, conditions_columns)
        if not columns_exist:
                self.error_status = True
                p[0] = f"ERROR: La columna {found_column} no existe en {p[3]}"
                return p[0]
        
        update_values = re.findall(r"'[A-Za-z\s]+'|\d+\.\d+|\d+", p[4])  
        
        conditions = p[6].strip().replace(" and ", " & ").replace(" or ", " | ").replace("=", "==")
        queried_table = table.query(conditions)
        mask = table.isin(queried_table.to_dict(orient='list')).all(axis=1)
        filtered_table = table[~mask]

        counter = 0
        for update_column in update_columns:
            queried_table[update_column] = update_values[counter]
            counter += 1
        
        result = pd.concat([filtered_table, queried_table])
        result.to_csv(TABLES_PATH + self.tables[p[2]], index=False)
        
        p[0] = f"Tabla {p[2]} actualizada con valores {p[4]} donde {p[6]}."
        
    def p_update_set(self, p: list[str]):
        'updation : UPDATE table SET updates'
        
        print("ESTO NO DEBERIA LLAMARSE")
        if not self.do_table_exist(p[2]):
            self.error_status = True
            p[0] = f"ERROR: La tabla {p[2]} no existe"
            return p[0]
        
        table = pd.read_csv(TABLES_PATH + self.tables[p[2]])
        columns = self.clean_columns_from_string(p[4])
        values = re.findall(r"'[A-Za-z]+'|\d+\.\d+|\d+", p[4])
        
        columns_exist, found_column = self.do_columns_exist(table, columns)
        if not columns_exist:
                self.error_status = True
                p[0] = f"ERROR: La columna {found_column} no existe en {p[3]}"
                return p[0]
        
        counter = 0
        for column in columns:
            table[column] = values[counter]
            counter += 1
            
        table.to_csv(TABLES_PATH + self.tables[p[2]], index=False)
        
        p[0] = f"Tabla {p[2]} actualizada con valores {p[4]}."

    def p_table(self, p: list[str]):
        'table : IDENTIFIER'
        p[0] = p[1]

    def p_expression(self, p: list[str]):
        '''expression : IDENTIFIER LESS NUMBER
                      | IDENTIFIER GREATER NUMBER
                      | IDENTIFIER EQUAL NUMBER
                      | IDENTIFIER EQUAL STRING'''
                      
        p[0] = f"{p[1]} {p[2]} {p[3]}"

    def p_expression_relational_expression(self, p: list[str]):
        '''expression : expression OR expression
                      | expression AND expression'''
        p[0] = f"{p[1]} {p[2]} {p[3]}"

    def p_expression_expression(self, p: list[str]):
        'expression : expression COMMA expression'
        p[0] = f"{p[1]}, {p[3]}"

    def p_columns_column(self, p: list[str]):
        'columns : column'
        p[0] = p[1]

    def p_columns_comma_column(self, p: list[str]):
        'columns : columns COMMA column'
        p[0] = f"{p[1]}, {p[3]}"

    def p_column(self, p: list[str]):
        'column : IDENTIFIER'
        p[0] = p[1]

    def p_fields(self, p: list[str]):
        'fields : field'
        p[0] = p[1]

    def p_fields_comma_field(self, p: list[str]):
        'fields : fields COMMA field'
        p[0] = f"{p[1]}, {p[3]}"

    def p_field(self, p: list[str]):
        '''field : STRING 
                 | NUMBER'''
        p[0] = p[1]

    def p_updates_update(self, p: list[str]):
        'updates : update'
        p[0] = p[1]

    def p_updates_comma_update(self, p: list[str]):
        'updates : updates COMMA update'
        p[0] = f"{p[1]}, {p[3]}"

    def p_update(self, p: list[str]):
        '''update : IDENTIFIER EQUAL STRING
                  | IDENTIFIER EQUAL NUMBER'''
        self.update_identifiers.append(p[1])
        p[0] = f"{p[1]} = {p[3]}"

    def p_error(self, p: list[str]):
        self.error_status = True
        self.query_result = "ERROR: Error de sintaxis"
        
    def get_tokens(self, input):
        tokens = {}
        counter = 0
        self.lexer.lexer.input(input)
        
        while(True):
            token = self.lexer.lexer.token()
            
            if token is not None:
                tokens.update({counter : {
                    "type": token.type,
                    "value": token.value
                }})
            counter += 1
            
            if not token:
                break
            
        return tokens
        
    def parse(self, input: str):
        tokens = self.get_tokens(input)
        self.error_status = False
        self.error_message = ""
        self.query_result = None
        self.parser.parse(input)
        
        if self.error_status:
            return False, self.query_result, tokens
        return True, self.query_result, tokens