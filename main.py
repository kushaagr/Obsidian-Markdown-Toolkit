import sys
import os
import glob
import operator
import re

from pathlib import Path
from datetime import datetime
from pprint import pprint

import lark
from lark import Lark, Transformer, v_args

from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.lexers import PygmentsLexer

from pygments.lexers.sql import SqlLexer

# os.chdir(os.environ['dev'] + '\\Python\\frontmatter-query-language')
os.chdir(Path(__file__).parent)
if 'dev' in os.environ.keys():
    sys.path.append(os.environ['dev'] + '\\Python\\')
    import debugmode as dbg
else:
    from types import SimpleNamespace
    dbg = SimpleNamespace(debug = lambda *_a, **_k: print("Debugmode is off.."))




FQLCompleter = WordCompleter([
    'SELECT', 'INSERT', 'CHANGE', 'QUIT',
    'FROM', 'INTO', 'IF EXISTS', 'SORT BY', 'WHERE',
    'ASC', 'DESC', 'MATCH', 'FUZZY MATCH', 'REGEX MATCH', 'MATCH'
])

statement_syntax = [
    R"SELECT <properties> FROM <folder-path> [ RECURSE ] [ WHERE <expression> ] [ SORT BY <property> ]""",
    R"INSERT <scalar-json-object> INTO <files-path> [ IF EXISTS ]",
    R"CHANGE <path>",
]


def read_text(path: Path) -> str:
    with open(path, encoding = 'cp850') as f:
        text = f.read()

    return text


def append_strings_to_file(file_path, string_list):
    try:
        with open(file_path, 'a') as file:
            for string in string_list:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                formatted_string = f"\n{timestamp}\n+{string}\n"
                file.write(formatted_string)
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def empty(text: str):
    return not bool(text.strip())

# Define custom operator functions
def matches_fx(pattern, value):
    return bool(re.search(pattern, value))

def notmatches_fx(pattern, value):
    return not bool(re.search(pattern, value))

def fuzzymatch_fx(pattern, value):
    # TODO ...
    return matches_fx(pattern, value)

# Define 'in' operator
def in_fx(key, value):
    # TODO ...
    # return value in x[key]
    pass

# Define 'notin' operator
def notin_fx(key, value):
    # TODO ...
    # return value not in x[key]
    pass

def filter_content(key, value, _input, op):
    if key not in _input:
        return False
    if not isinstance(_input[key], list):
        return operators[op](value, _input[key])
    else:
        binary_fx = lambda x: operators[op](x, value)
        return len(list( filter(binary_fx, _input[key]) )) > 0        

# Create a mapping of operator names to operator functions
operators = {
    'eq': operator.eq,
    'ne': operator.ne,
    'lt': operator.lt,
    'gt': operator.gt,
    'le': operator.le,
    'ge': operator.ge,
    'regex_match': matches_fx,
    'regex_no_match': notmatches_fx,
    'in': in_fx,
    'not_in': notin_fx,
    'fuzzy_match': fuzzymatch_fx
    # Add more custom operators as needed
}

class FqlAstTransformer(Transformer):
    
    def resource_path(self, tokens):
        resource = tokens[0]['path']
        if len(tokens) > 1:
            # path, wildcard = tokens
            wildcard = tokens[1]
            # path = path['path']
            wildcard = wildcard or ''
            # resource = path + wildcard
            resource = resource + wildcard
            
        return {'resource': resource}


    def files(self, tokens):
        path = tokens[0]['path']
        pattern = tokens[1]
        resource = path + pattern
        return {'resource': resource}
        

    # def where_clause(self, filter_expression):
    #     return filter_expression[0]

    # def _filter(filter_expression, input: list):
    #     pass
    

    def _isin_parsed_data(key, value):
        pass


    def sort_clause(self, tokens):
        # reverse = tokens[-1].upper() == "DESC"
        *props, descending = tokens
        descending = str(descending).upper() == 'DESC'
        return {"props":props, "desc": descending}


    def select_stmt(self, tokens):
        props_dict, from_dict, recurse, where_expression, sortby_props = tokens
        props = props_dict['properties']
        pattern_path = from_dict['resource']
        # get items using glob.glob AND from_where
        #   if recurse is on then do it recursively
        #   check item is file
        if recurse:
            pattern_path = pattern_path.replace('/*', '**/*')
        rawfiles = [os.path.relpath(file) 
            for file in glob.glob(pattern_path, recursive=recurse) 
            if os.path.isfile(file)
        ]
        # return f"SELECT_STMT return {(rawfiles)}"

        blocks = []                
        # parse the file(s)
        from Mdyaml_Transformer import FmAstTransformer

        mdgrammar = read_text('./mdfile-grammar.lark')
        mdparser = Lark(mdgrammar,
                        maybe_placeholders=False,
                        # parser='lalr',
                        parser='earley',
                        )
        for file in rawfiles:
            content = read_text(file)
            # dbg.debugset = "file-content"
            dbg.debug("*"*5,"file-content", debug_group="file-content")
            dbg.debug(content, debug_group="file-content")

            if empty(content):
                dbg.debug(f"(Info) Empty file: {file} ..Skipping!")
                continue

            # dbg.debugset = "file-name"
            dbg.debug("*"*5,"file-name", debug_group="file-name")
            dbg.debug(f"Processing file: {file}", debug_group="file-name")
            tree = mdparser.parse(content)
            
            # dbg.debugset = 'fmblock'
            dbg.debug("*"*5, "fmblock", "*"*5, debug_group='fmblock')
            dbg.debug(tree, debug_group='fmblock')
            dbg.debug(tree.pretty(), debug_group='fmblock')
            fmblock = FmAstTransformer().transform(tree)
            if not isinstance(fmblock, dict):
                dbg.debug(f"(Info) No frontmatter found: {file} ..Skipping!")
                continue

            dbg.debugset = "parsed-content-short"
            dbg.debug(5*"*", "parsed-content-short", 5*"*", debug_group="parsed-content-short")
            dbg.debug(type(fmblock), fmblock['frontmatter'], debug_group="parsed-content-short")
            # dbg.debug(fmblock['frontmatter'], debug_group="parsed-content-short")

            # def add_block:
                # Add file to filters_files array
                # Add block to blocks array
                # Meaning keep two arrays so that blocks are easier to sort
                # pass 
            add_block = lambda: blocks.append((file, fmblock['frontmatter']))

            # if given a where_clause
            # filter the parse input
            if where_expression:
                op = next(iter(where_expression))
                prop, value = where_expression[op]
                
                # dbg.debugset = 'where-clause-details'
                dbg.debug(f"{'*'*3} where_expression", debug_group='where-clause-details')
                dbg.debug(f"{op=} {prop=} {value=}", debug_group='where-clause-details')

                if op in operators:
                    pick = filter_content(prop, value, fmblock['frontmatter'], op)
                    if pick:
                        add_block()
                else:
                    print(f"Error : Operator {op} not found", file=sys.stderr)
            else:
                add_block()
            
    
        dbg.debugset = 'filtered-data'
        dbg.debug(f"{'*' * 3}filtered-data", debug_group="filtered-data")
        dbg.debug(blocks, debug_group="filtered-data")

        # if given a sort_clause
        # sort the input
        if sortby_props:
            
            sorting_keys = sortby_props['props']
            desc = sortby_props['desc']

            # Define a custom sorting key function
            def custom_sort_key(file_with_metadata):
                d = file_with_metadata[1]
                # Create a tuple of values for the specified keys
                return tuple(d.get(key, '~') for key in sorting_keys)

            # Sort the list of dictionaries using the custom key function
            block = sorted(blocks, key=custom_sort_key)

            dbg.debugset = 'sorted-data'
            dbg.debug(f"{'*' * 3}sorted-data", debug_group="sorted-data")
            dbg.debug(blocks, debug_group="sorted-data")
        

        # finally, if properties contain "*":
        # print all
        # else for each parsed item:
        #   for all props: if prop in parsed_item[frontmatter].keys():
        #       print the key-value pair
        #   or
        #   filter parsed_item[frontmatter].keys() such that item in props 

        def __collape_region():
            pass
            # def f(t):
            #     di = t[1]
            #     k = di.keys()
            #     return t if k in props else None

            # def f(pair):
            #     def g(x):
            #         k, i = x
            #         return x if k in props else None
            #     di = pair[1]
            #     return list(filter(g, di.items()))
        
        # selected = list( filter(f, blocks) ) if props[0].strip() != '*' else blocks
        # print(f"{selected=}")

        def f(t):
            return props[0] == '*' or any(prop in props for prop in t[1])

        # for item in selected:
        # if len(filtered) > 0:
        select_all_props = props[0] == '*'
        for item in filter(f, blocks):
            filename = item[0]
            print( filename )
            tablength = 2
            tabs = " " * tablength
            # for key_property in item[1].items():
            #     k, v = key_property
            #     if k in props or props[0] == '*':
            #     # if True:
            #         print(tabs, f"{k}: {v}", sep='')
            if select_all_props:
                props = list(item[1].keys())
                print("*"*(tablength-1), props)
            for prop in props:
                if item[1].get(prop):
                    print(tabs, f"{prop}: {item[1][prop]}", sep='')
            

        dbg.debugset = 'select-details'
        dbg.debug("*"*3, "select-details", debug_group="select-details")
        dbg.debug('(--', props, from_dict, recurse, where_expression, sortby_props, '--)', debug_group='select-details')
        return props, from_dict, recurse, where_expression, sortby_props

    # def pair(self, tokens):
    #     return dict()

    def key_value_list(self, tokens):
        return { "items": list(tokens) }


    def insert_stmt(self, tokens):
        items_dict, into_dict, if_exists, where_expression = tokens
        items = items_dict['items']
        pattern_path = into_dict['resource']

        # Note: recursive flag in glob enables recursion only when "**" is in pattern 
        rawfiles = [os.path.relpath(file) 
            for file in glob.glob(pattern_path, recursive=True) 
            if os.path.isfile(file)
        ]
        # return f"SELECT_STMT return {(rawfiles)}"

        #TODO: Implement if_exists flag
    
        blocks = []                
        # parse the file(s)
        from Mdyaml_Transformer import FmAstTransformer

        mdgrammar = read_text('./mdfile-grammar.lark')
        mdparser = Lark(mdgrammar,
                        maybe_placeholders=False,
                        # parser='lalr',
                        parser='earley',
                        )
        if True:
            for file in rawfiles:
                content = read_text(file)

                tree = mdparser.parse(content)
                fmblock = FmAstTransformer().transform(tree)
                if not isinstance(fmblock, dict):
                    dbg.debug(f"(Info) No frontmatter found: {file} ..Skipping!")
                    continue

                dbg.debugset = "parsed-content-short"
                dbg.debug(5*"*", "parsed-content-short", 5*"*", debug_group="parsed-content-short")
                dbg.debug(type(fmblock), fmblock['frontmatter'], debug_group="parsed-content-short")

                fm = fmblock['frontmatter']
                bd = fmblock['body']

                # add_content = lambda: blocks.append((file, fmblock['frontmatter']))
                def add_content():
                    for item in items:
                        fm[item[0]] = item[1]
                
                if where_expression:
                    op = next(iter(where_expression))
                    prop, value = where_expression[op]
                    
                    # dbg.debugset = 'where-clause-details'
                    dbg.debug(f"{'*'*3} where_expression", debug_group='where-clause-details')
                    dbg.debug(f"{op=} {prop=} {value=}", debug_group='where-clause-details')

                    if op in operators:
                        pick = filter_content(prop, value, fmblock['frontmatter'], op)
                        if pick:
                            add_content()
                    else:
                        print(f"Error : Operator {op} not found", file=sys.stderr)
                else:
                    add_content()

                def formatter(kv):
                    k, v = kv
                    if isinstance(v, list):
                        str_list = [f"{k}:"]
                        return '\n'.join(str_list + [f"\t- {item}" for item in v]) + "\n"
                    # if isinstance(v, str):
                    return f"{k}: {v}\n"

                with open(file, 'w') as f:
                    # print(list(map(formatter, fm.items())))
                    f.write("---\n")
                    f.writelines( list(map(formatter, fm.items())) )
                    f.write("---\n")
                    f.write("\n")
                    f.writelines(bd)
                    # f.write(bd)
                    print(f"{fm=}")
                    print(f"{type(bd)=}")
                    print(f"{bd=}")

    # insert_stmt = lambda _, x: x

    def cd_stmt(self, tokens):
        try:
            path = tokens[0]['path']
            os.chdir(path)
            print(f"Current working directory: {path}")
        except FileNotFoundError as ffe:
            print(f"The system cannot find the path specified: {path}", file=sys.stderr)

    def quit_stmt(self, tokens):
        print("आपका दिन शुभ रहे। " + " (Have a nice day!)")
        raise SystemExit
    
    NUMBER = float
    DATETIME = datetime.fromisoformat
    BOOLEAN = bool
    NULL = lambda self, _: None
    STRING = lambda _, x: str(x)[1:-1]
    VARIABLE_STRING = lambda _, x: str(x)
    
    RECURSE_FLAG = bool  
    IF_EXISTS_FLAG = bool 

    PROPERTY = lambda _, x: x.strip("\"'")
    ASTERISK = str
    WILDCARD_TEXT = str
    ORDER = str

    OPERATOR = str        
    # operator = lambda _, x: dir(x[0])
    # expression = lambda _, x: {"expression":[ str(x[0].data), x[0].children ]}
    expression = lambda _, x: {str(x[0].data) : x[0].children}

    properties = lambda _, x: {"properties": x}
    array = list
    # simple_value = lambda _, x: {"simv": x[0]}
    simple_value = lambda _, x: x[0]
    path = lambda self, value: { "path": "".join(value) }
    path_with_environment_variable = lambda self, x: (
        os.environ.get(x[1]) + ( "".join(x[2:]) if len(x) > 2 else "")
    )
    template_variable = lambda _, x: { 
        'date.now': datetime.today().strftime('%Y-%m-%d'),
        'time.now': datetime.today().strftime('%H:%M:%S'),
    }.get(x[0], '')
    pair = lambda _, x: tuple(x)
    
    def __collape_region():
        pass
        # RECURSE_FLAG = lambda _, x: {"recurse": bool(x)}
        # IF_EXISTS_FLAG = lambda _, x: {"if_exists": bool(x)}
        
        # WILDCARD_TEXT = DOT = SLASH = DIRECTORY = str


        # def path(self, value):
        #     return "".join(value)

        # resource_path = lambda self, value: { "resource": "".join(value[0]['path'] )}
        # resource_path = lambda self, value: { 
        #     # "resource": value[0]['path'] if len(value) == 1 else ( "".join(value[0]['path']) + value[1:][0] ) 
        #     "resource": value[0]['path'] if len(value) == 1 else "".join([value[0]['path']] + value[1:]) 
        # }
        # resource_path: 
        # where_clause
        # select_stmt = lambda _, tokens: { k:v for obj in tokens for k,v in obj.items() }
        # select_stmt = lambda _, tokens: tokens


    def __collape_region():
        pass
        # DIRECTORY = lambda _, x: print("Details of DIRECTORY", f"{type(x)=}", str(x)) 
        # DIRECTORY = lambda _, x: str(x)
        # relative_path: v_args(inline=True)(lambda _, x: print("Details of relative_path", f"{type(x)=}", x))
        # relative_path: lambda self, x: "".join(x)
        # relative_path: lambda _, x: print("Details of relative_path", f"{type(x)=}", x)
        
        # resource_path: lambda _, x: print("Details of resource_path", f"{type(x)=}", x)
        # absolute_path: lambda _, x: print("Details of absolute_path", f"{type(x)=}", x)
        # windows_path: lambda _, x: print("Details of windows_path", f"{type(x)=}", x)
        # linux_path: lambda _, x: print("Details of linux_path", f"{type(x)=}", x)
        # quoted_resource_path: lambda _, x: print("Details of quoted_resource_path", f"{type(x)=}", x)
        # quoted_path: lambda _, x: print("Details of quoted_path", f"{type(x)=}", x)
        # path: lambda _, x: print("Details of path", f"{type(x)=}", x)
        # path_with_environment_variable: lambda _, x: print("Details of path_with_environment_variable", f"{type(x)=}", x)
        # files: lambda _, x: print("Details of file", f"{type(x)=}", x)
        # select_stmt: lambda _,x : print("SELECT STATEMENT")

        # def relative_path(self, tokens):
        #     # dbg.debugset = "misc"
        #     dbg.debug("Details of relative_path", f"{type(tokens)=}", tokens)
        #     print("Details of relative_path", f"{type(tokens)=}", tokens)
        #     return tokens


if __name__ == '__main__':
    dbg.debugmode = True
    # dbg.debugmode = False

    dbg.debug(os.getcwd())
    dbg.debug("File is in:", __file__)

    HISTORY_FILE = 'FroqlHistory.txt'

    fql_grammar = read_text('./fql-grammar.lark')
    # fql_grammar = read_text('./simple-test-grammar.lark')
    # fql_grammar = read_text('./json-grammar.lark')
    # fql_grammar = read_text('./lalr-fql-grammar.lark')
    # dbg.debug(fql_grammar)

    fql_parser = Lark(fql_grammar,
                        # maybe_placeholders=False,
                        maybe_placeholders=True,
                        # parser='lalr',
                        parser='earley',
                        ambiguity='explicit',
                        
                    )

    print("Working in " + os.getcwd())


    if dbg.debugmode:
        test_stmts = [
            # R"SELECT * FROM './Notes/*' ",
            # R"SELECT Author, created FROM './Notes/*' ",
            # R"SELECT * FROM './Notes/*.md'",
            R"SELECT * FROM './Notes/Find Factor Algorithm.md'",
            # R"""SELECT * FROM './Notes/*.md' WHERE "Up link" = null """,
            # R"""SELECT * FROM './Notes/*' RECURSE WHERE Author = "kushaagr" """,
            # R"""SELECT * FROM './Notes/*' RECURSE WHERE "Date (created)" = 2023-09-19""",
            # R"""SELECT * FROM './Notes/F*.md' RECURSE WHERE Author IN ["Chat GPT (September 25 version)", "Chat GPT (August 3 version)"]""",
            # R"""SELECT * FROM './Notes/*' RECURSE WHERE Author NOT IN ["Chat GPT (September 25 version)", "Chat GPT (August 3 version)"]""",
            # R"""SELECT * FROM './Notes/*.md' RECURSE WHERE Author = "kushaagr" SORT BY Author ASC""",
            # R"""SELECT * FROM './Notes/*.md' RECURSE WHERE Author = "kushaagr" SORT BY Author ASC""",
            # R"""SELECT tags, "Author" FROM './Notes/*.md' RECURSE WHERE Author = "kushaagr" SORT BY Author ASC""",
            # R"SELECT * FROM './Notes/*.md' sort by Author, created",

            # # R"CHANGE",
            # R"CHANGE .",
            # R"CHANGE c:\users\kusha\documents\dev\ ",
            # R"CHANGE 'c:\users\kusha\documents\dev\' ",
            # R"CHANGE '$dev\python\'",
            # R"CHANGE /usr/home/dev/",

            # R"INSERT {} INTO ./Notes/*.md ",
            R"""INSERT {test: "Value I"} INTO './Notes/Find Factor Algorithm.md' """, 
            R"""INSERT {test: "Value I", count: 1} INTO './Notes/Find Factor Algorithm.md' IF EXISTS """, 
            R"""INSERT {test_1: "Value II", date: {{date.now}} } INTO './Notes/Find Factor Algorithm.md' """, 
            # R"INSERT {} INTO './Notes/*.md' ",
            # R"""INSERT {} INTO "./Notes/*.md" """,
            # R"""INSERT {} INTO ./Notes/* IF EXISTS WHERE Author = "kushaagr" """,
            # # R"INSERT {} INTO ./Notes/",
 
            # "QUIT",
            # "QUIT;",

        ]
        for statement in test_stmts:
            dbg.debugset = "first"
            dbg.debug()
            
            dbg.debugset='stmt'
            dbg.debug("Tree for:", statement, debug_group='stmt')

            dbg.debugset = 'tree-testing'
            tree = fql_parser.parse(statement)
            dbg.debug("Pretty parsed tree..", debug_group='tree-testing') 
            if (isinstance(tree, lark.tree.Tree)):
                dbg.debug(tree.pretty(), debug_group='tree-testing')
                pass
            else:
                dbg.debug(f"{isinstance(tree, lark.tree.Tree)=}", debug_group='tree-testing')

            actiondata = FqlAstTransformer().transform(tree)
            dbg.debug("After transform..", debug_group='tree-testing')
            if (isinstance(actiondata, lark.tree.Tree)):
                dbg.debug(actiondata.pretty(), debug_group='tree-testing')
            else:
                dbg.debug(f"{isinstance(actiondata, lark.tree.Tree)=}", debug_group='tree-testing')
                

            dbg.debugset = "raw"
            dbg.debug("RAW DATA", debug_group="raw")
            dbg.debug("After transorm (raw)..")
            dbg.debug(actiondata, debug_group="raw")
            
            # dbg.debugset = "types"
            # dbg.debug("TYPES", debug_group="types")
            dbg.debug(f"{type(tree)=}", debug_group="types")
            dbg.debug(f"{type(actiondata)=}", debug_group="types")

            # dbg.debugset = "isinstance"
            dbg.debug("isinstance", debug_group="isinstance")
            dbg.debug(f"{isinstance(tree, lark.tree.Tree)=}", debug_group="isinstance")


    print("Hint: Try typing one of: SELECT | INSERT | CHANGE | QUIT")
    while True and not dbg.debugmode:
        try:
            statement = prompt(u'froql> ',
                        history=FileHistory(HISTORY_FILE),
                        auto_suggest=AutoSuggestFromHistory(),
                        completer=FQLCompleter,
                        lexer=PygmentsLexer(SqlLexer)
                        )
            tree = fql_parser.parse(statement)
            print(tree.pretty())
        except Exception as e:
            print(type(e), e)
        except KeyboardInterrupt:
            # print("<aapka-din-shubh-rahe -- in-hindi>")
            # print("Have a great day.")
            # print("Thank you for trying out.")
            append_strings_to_file(HISTORY_FILE, statement_syntax)
            print("Graceful exit..")
            raise SystemExit
