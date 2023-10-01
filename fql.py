import sys
import os
from pathlib import Path
from datetime import datetime

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
    r"SELECT <properties> FROM <folder-path> [ RECURSE ] [ WHERE <expression> ] [ SORT BY <property> ]",
    r"INSERT <scalar-json-object> INTO <files-path> [ IF EXISTS ]",
    r"CHANGE <path>",
]


def read_grammar(path: Path) -> str:
    with open(path) as f:
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


if __name__ == '__main__':
    dbg.debugmode = True
    dbg.debugmode = False

    dbg.debug(os.getcwd())
    dbg.debug("File is in:", __file__)

    HISTORY_FILE = 'FroqlHistory.txt'

    fql_grammar = read_grammar('./fql-grammar.lark')
    # fql_grammar = read_grammar('./simple-test-grammar.lark')
    # fql_grammar = read_grammar('./json-grammar.lark')
    # fql_grammar = read_grammar('./lalr-fql-grammar.lark')
    # dbg.debug(fql_grammar)

    fql_parser = Lark(fql_grammar,
                        maybe_placeholders=False,
                        # parser='lalr',
                        parser='earley',
                        ambiguity='explicit',
                    )

    print("Working in " + os.getcwd())


    if dbg.debugmode:
        test_stmts = [
            R"SELECT * FROM './Notes/' ",
            R"SELECT * FROM './Notes/*.md'",
            R"SELECT * FROM './Notes/Find Factor Algorithm.md'",
            R"""SELECT * FROM './Notes/' RECURSE WHERE Author = "kushaagr" """,
            R"""SELECT * FROM './Notes/' RECURSE WHERE "Date (created)" = 2023-09-19""",
            R"""SELECT * FROM './Notes/' RECURSE WHERE Author IN ["Chat GPT (September 25 version)", "Chat GPT (August 3 version)"]""",
            R"""SELECT * FROM './Notes/' RECURSE WHERE Author = "kushaagr" SORT BY Author ASC""",

            # R"CHANGE",
            R"CHANGE .",
            R"CHANGE c:\users\kusha\documents\dev\ ",
            R"CHANGE 'c:\users\kusha\documents\dev\' ",
            R"CHANGE '$dev\python\'",
            R"CHANGE /usr/home/dev/",

            R"INSERT {} INTO ./Notes/*.md ",
            R"INSERT {} INTO './Notes/*.md' ",
            R"""INSERT {} INTO "./Notes/*.md" """,
            R"""INSERT {} INTO ./Notes/* IF EXISTS WHERE Author = "kushaagr" """,
            # R"INSERT {} INTO ./Notes/",

            "QUIT",
            "QUIT;",

        ]
        for statement in test_stmts:
            dbg.debug("Tree for:", statement)
            tree = fql_parser.parse(statement)
            dbg.debug(tree.pretty())    


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
