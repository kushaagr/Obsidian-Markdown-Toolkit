import glob
import os
import sys
import datetime as dt

from pathlib import Path
from lark import Lark, Transformer, v_args

from pprint import pprint
os.chdir(Path(__file__).parent)
if 'dev' in os.environ.keys():
    sys.path.append(os.environ['dev'] + '\\Python\\')
    import debugmode as dbg
else:
    from types import SimpleNamespace
    dbg = SimpleNamespace(debug=print)


class FroMaAstTransformer(Transformer):
    PROPERTY = TEXT_LINE = BLANK_LINE = STRING = str
    NUMBER = float
    BOOLEAN = bool
    DATETIME = dt.datetime.fromisoformat
    indented_seq = list
    # yaml_block = list
    # yaml_block = lambda _, r: print("yaml block details", type(r), r)
    # kvpair = lambda self, pair: print("kvpair details:", type(pair), pair)
    kvpair = lambda self, pair: dict( [tuple(pair)] ) # List of couple (touple of 2)
    inline_seq = lambda self, s: s[1:-1].split(',')
    yaml_block = lambda _, list_of_props: { 'frontmatter': list_of_props }
    body = lambda self, lines: { "body" : "".join(lines)}
    # body = lambda self, lines: "".join(lines)
    # frontmatter = list
    # start = lambda _, content: { k:v for k, v in [items for items in content] }
    start = lambda _, content: { k:v for mapping in content for k,v in mapping.items() }

    # def start(self, content):
    #     l = [k for dicti in content for k,v in dicti.items()]
    #     print("start details", f"{len(l)=}, {l}")
    

def read_text(path: Path) -> str:
    with open(path) as f:
        text = f.read()
    return text

if __name__ == '__main__':
    dbg.debugmode = True
    # dbg.debugmode = False
    dbg.debugset = 'fmblock'
    dbg.debugset = 'final-result'
    dbg.debugset = None

    dbg.debug(os.getcwd())
    dbg.debug("File is in:", __file__)

    mdgrammar = read_text('./mdfile-grammar.lark')
    mdparser = Lark(mdgrammar,
                    maybe_placeholders=False,
                    # parser='lalr',
                    parser='earley',
                    ambiguity='explicit'
                    )

    grammar = read_text('./Notes/Find Factor Algorithm.md')
    tree = mdparser.parse(grammar)
    dbg.debug(tree.pretty(), debug_group='fmblock')
    fmblock = FroMaAstTransformer().transform(tree)
    dbg.debug(f"{type(fmblock)=}", debug_group='fmblock')
    # print(f"{dir(fmblock)=}")
    # dbg.debug(f"{type(fmblock.children)=}, {len(fmblock.children)=}", debug_group='fmblock')
    # pprint(f"{fmblock.children=}")
    
    dbg.debug(f"{type(fmblock)=}", debug_group='final-result')
    # dbg.debug(fmblock, debug_group="final-result")
    # dbg.debug(fmblock.pretty(), debug_group="final-result")

    pprint(fmblock)
    print(fmblock['frontmatter'])