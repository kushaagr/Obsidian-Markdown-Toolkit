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
    dbg = SimpleNamespace(debug = lambda *_a, **_k: print("Debugmode is off.."))


class FroMaAstTransformer(Transformer):
    TEXT_LINE = BLANK_LINE = EMPTY_LINE = lambda _, l: "".join(l)
    text_line = blank_line = empty_line = lambda _, l: "".join(l)
    LINE_OF_TEXT = ENDL = lambda _, l: "".join(l)
    # PROPERTY = CNAME = STRING = lambda _, x: str(x).strip()
    STRING = lambda _, x: str(x).strip()
    # key_name = lambda _, x: str(x).strip()
    # KEY_NAME = key_name = lambda _, x: print(f"KEY_NAME details: {x} {type(x)} str(x): {str(x)}") or str(x).strip()
    KEY_NAME = key_name = lambda _, x: str(x)
    # property = lambda _, x: str(x)
    DETECT_NO_FRONTMATTER = str
    first_line = lambda self, lines: { "header" : "".join(lines) }

    NUMBER = float
    boolean = bool
    true = lambda _, x: True
    false = lambda _, x: False
    DATETIME = dt.datetime.fromisoformat
    indented_seq = list
    # yaml_block = list
    # yaml_block = lambda _, r: print("yaml block details", type(r), r)
    # kvpair = lambda self, pair: print("kvpair details:", type(pair), pair)
    # kvpair = lambda self, pair: dict( [tuple(pair)] ) # List of couple (touple of 2)
    # kvpair = lambda self, pair: print(f"kv-details: p0: {type(pair[0])}, {pair[0]} len: {len(pair[0])}\n {type(pair)}, {pair}") or { pair[0]: pair[1] } 
    kvpair = lambda self, pair: { pair[0]: pair[1] } 
    inline_seq = lambda self, s: s[1:-1].split(',')
    empty_file = lambda _, x: {'frontmatter': {}, 'body': x}
    no_metadata = lambda _,x: {'frontmatter': {}, 'body': x[0]['header'] + (x[1]['body'] if len(x) > 2 else '')}
    # yaml_block = lambda _, list_of_props: { 'frontmatter': list_of_props[0] }
    # yaml_block = lambda _, list_of_props: { 'frontmatter': list_of_props }
    yaml_block = lambda _, list_of_props: { 
        'frontmatter': { 
            k:v for obj in list_of_props for k,v in obj.items() 
    }}
    # body = lambda self, lines: print(f"BODY-DETAILS: {type(lines)}, {len(lines)}, {type(''.join(lines))}") or { "body" : "".join(lines) }
    body = lambda self, lines: { "body" : "".join(lines) }
    # body = lambda self, lines: "".join(lines)
    # frontmatter = list
    # start = lambda _, content: content
    # start = lambda _, content: { k:v for k, v in [items for items in content] }
    start = lambda _, content: { 
        k:v for mapping in content for k,v in mapping.items() 
    }

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
    # dbg.debugset = 'final-result'
    # dbg.debugset = None

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
    # grammar = read_text('./Notes/(+) LESS IS MORE.md')
    # grammar = read_text('./Notes/ChatGPT logo SVG.md')
    # grammar = read_text('./Notes/Create images of multiple sizes with Python and PIL.md')
    # grammar = read_text('./Notes/Curl command for Danbooru API.md')
    tree = mdparser.parse(grammar)
    
    dbg.debugset = 'fmblock'
    dbg.debug(tree, debug_group='fmblock')
    dbg.debug(type(tree), debug_group='fmblock')
    
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
    # print(fmblock['frontmatter'])
    # print(fmblock['frontmatter'].keys())
    # print(fmblock['frontmatter']["['Author']"])