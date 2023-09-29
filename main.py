import glob
import os
import sys

from pathlib import Path
from lark import Lark, Transformer, v_args

os.chdir(Path(__file__).parent)
if 'dev' in os.environ.keys():
    sys.path.append(os.environ['dev'] + '\\Python\\')
    import debugmode as dbg
else:
    from types import SimpleNamespace
    dbg = SimpleNamespace(debug=print)


def read_text(path: Path) -> str:
    with open(path) as f:
        text = f.read()
    return text

if __name__ == '__main__':
    dbg.debugmode = True
    dbg.debugmode = False

    dbg.debug(os.getcwd())
    dbg.debug("File is in:", __file__)

    mdgrammar = read_text('./mdfile-grammar.lark')
    mdparser = Lark(mdgrammar,
                    maybe_placeholders=False,
                    # parser='lalr',
                    parser='earley',
                    ambiguity='explicit'
                    )

    print(
        mdparser.parse(read_text('./Notes/Find Factor Algorithm.md'))
        .pretty()
    )