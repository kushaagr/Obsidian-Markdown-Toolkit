import sys
import os
from pathlib import Path

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
    dbg = SimpleNamespace(debug=print)




FQLCompleter = WordCompleter([
    'SELECT', 'INSERT', 'CHANGE', 'QUIT',
    'FROM', 'INTO', 'IF EXISTS', 'SORT BY', 'WHERE',
    'ASC', 'DESC', 'MATCH', 'FUZZY MATCH', 'REGEX MATCH'
])


def read_grammar(path: Path) -> str:
    with open(path) as f:
        text = f.read()

    return text



if __name__ == '__main__':
    dbg.debugmode = True
    dbg.debugmode = False

    dbg.debug(os.getcwd())
    dbg.debug("File is in:", __file__)

    fql_grammar = read_grammar('./grammar.lark')
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
    while True and not dbg.debugmode:
        try:
            statement = prompt(u'froql> ',
                        history=FileHistory('FroqlHistory.txt'),
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
            print("Graceful exit..")
            raise SystemExit
