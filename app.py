import os
import sys
from pathlib import Path
from pprint import pprint
from datetime import datetime

from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.lexers import PygmentsLexer

from prompt_toolkit.styles.pygments import style_from_pygments_cls
from pygments.styles import get_style_by_name
from pygments.lexers.sql import SqlLexer

import lark
from lark import Lark, v_args

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
    r"SELECT <properties> FROM <folder-path> [ RECURSE ] [ WHERE <expression> ] [ SORT BY <property> ]",
    r"INSERT <scalar-json-object> INTO <files-path> [ IF EXISTS ]",
    r"CHANGE <path>",
]


def read_grammar(path: Path) -> str:
    with open(path) as f:
        text = f.read()
    return text


def append_strings_to_file(file_path, string_list):
    if dbg.debugmode:
        dbg.debug("Skipping history hack for debug mode...")
        return
    try:
        with open(file_path, 'a') as file:
            for string in string_list:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                formatted_string = f"\n{timestamp}\n+{string}\n"
                file.write(formatted_string)
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == '__main__':
    dbg.debugmode = True
    dbg.debugmode = False
    HISTORY_FILE = 'FroqlHistory.txt'

    fql_grammar = read_grammar(Path(__file__).parent / 'fql-grammar.lark')
    fql_parser = Lark(fql_grammar,
                        maybe_placeholders=True,
                        # parser='lalr',
                        parser='earley',
                        ambiguity='explicit',
                    )

    
    print("Working in", os.getcwd())
    dbg.debug("Debugmode =", dbg.debugmode)
    while True and dbg.debugset != 'non-interactive':
        try:
            statement = prompt(u'froql> ',
                        history=FileHistory(HISTORY_FILE),
                        auto_suggest=AutoSuggestFromHistory(),
                        completer=FQLCompleter,
                        lexer=PygmentsLexer(SqlLexer),
                        style=style_from_pygments_cls(get_style_by_name('dracula'))
                        )
            tree = fql_parser.parse(statement)
            
            dbg.debugset = 'pretty-tree'
            dbg.debug("*"*3, "pretty-tree", debug_group='pretty-tree')
            dbg.debug(tree.pretty(), debug_group='pretty-tree')

            from Froql_Transformer import FqlAstTransformer

            actiondata = FqlAstTransformer().transform(tree)
            # print(actiondata)

            dbg.debugset = 'tree-testing'
            dbg.debug("After transform..", debug_group='tree-testing')
            if (isinstance(actiondata, lark.tree.Tree)):
                dbg.debug(actiondata.pretty(), debug_group='tree-testing')
            else:
                dbg.debug(f"{isinstance(actiondata, lark.tree.Tree)=}", debug_group='tree-testing')
                

            dbg.debugset = "raw"
            dbg.debug("RAW DATA", debug_group="raw")
            dbg.debug("After transorm (raw)..")
            dbg.debug(actiondata, debug_group="raw")
            
            dbg.debugset = "types"
            # dbg.debug("TYPES", debug_group="types")
            dbg.debug(f"{type(tree)=}", debug_group="types")
            dbg.debug(f"{type(actiondata)=}", debug_group="types")

            # dbg.debugset = "isinstance"
            dbg.debug("isinstance", debug_group="isinstance")
            dbg.debug(f"{isinstance(tree, lark.tree.Tree)=}", debug_group="isinstance")

        # Note: Comment below 2 lines when debugging
        except Exception as e:
            print(type(e), e)
        except KeyboardInterrupt:
            # print("<aapka-din-shubh-rahe -- in-hindi>")
            # print("Have a great day.")
            # print("Thank you for trying out.")
            append_strings_to_file(HISTORY_FILE, statement_syntax)
            print("Graceful exit..")
            raise SystemExit
