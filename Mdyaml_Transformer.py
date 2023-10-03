import datetime as dt
from lark import Transformer

class FmAstTransformer(Transformer):
    TEXT_LINE = BLANK_LINE = EMPTY_LINE = lambda _, l: "".join(l)
    LINE_OF_TEXT = ENDL = lambda _, l: "".join(l)
    STRING = lambda _, x: str(x).strip()
    # key_name = lambda _, x: str(x).strip()
    # KEY_NAME = key_name = lambda _, x: print(f"KEY_NAME details: {x} {type(x)} str(x): {str(x)}") or str(x).strip()
    KEY_NAME = key_name = lambda _, x: str(x)
    # property = lambda _, x: str(x)
    DETECT_NO_FRONTMATTER = str
    text_line = blank_line = empty_line = lambda _, l: "".join(l)
    first_line = lambda self, lines: { "header" : "".join(lines) }

    NUMBER = float
    STRING = lambda _, x: str(x).strip()
    KEY_NAME = key_name = lambda _, x: str(x)

    boolean = bool
    true = lambda _, x: True
    false = lambda _, x: False
    DATETIME = dt.datetime.fromisoformat
    indented_seq = list
    # yaml_block = list
    # yaml_block = lambda _, r: print("yaml block details", type(r), r)
    # kvpair = lambda self, pair: print("kvpair details:", type(pair), pair)
    # kvpair = lambda self, pair: dict( [tuple(pair)] ) # List of couple (touple of 2)
    kvpair = lambda self, pair: { pair[0]: pair[1] } 
    inline_seq = lambda self, s: s[1:-1].split(',')
    # yaml_block = lambda _, list_of_props: { 'frontmatter': list_of_props }
    empty_file = lambda _, x: {'frontmatter': {}, 'body': x}
    no_metadata = lambda _,x: {'frontmatter': {}, 'body': x[0]['header'] + (x[1]['body'] if len(x) > 2 else '')}
    yaml_block = lambda _, list_of_props: { 
        'frontmatter': { 
            k:v for obj in list_of_props for k,v in obj.items() 
    }}
    body = lambda self, lines: { "body" : "".join(lines) }
    # body = lambda self, lines: "".join(lines)
    # frontmatter = list
    # start = lambda _, content: { k:v for k, v in [items for items in content] }
    start = lambda _, content: { 
        k:v for mapping in content for k,v in mapping.items() 
    }