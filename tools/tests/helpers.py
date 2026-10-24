"""站点测试公用工具：读取文章、解析构建产物。"""
import re
import tomllib
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / '.build'

EXPECTED = {'新易体系': 10, '量子与易学': 11, '三进制与九卦': 8,
            '古典研究': 5, '科学前沿': 5, '哲思与赋': 3}


def split_front_matter(text):
    """返回 (含分隔线的 front matter, 正文)。"""
    m = re.match(r'(\+\+\+\n.*?\n\+\+\+\n|---\n.*?\n---\n)', text, re.S)
    if not m:
        return '', text
    return m.group(1), text[m.end():]


def _parse_yaml(fm):
    meta = {}
    for line in fm.splitlines():
        m = re.match(r'(\w+):\s*(.*)$', line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if val.startswith('['):
            meta[key] = re.findall(r'["\']([^"\']*)["\']', val)
        elif val in ('true', 'false'):
            meta[key] = val == 'true'
        else:
            meta[key] = val.strip('"\'')
    return meta


@dataclass
class Post:
    path: Path
    slug: str
    meta: dict
    body: str


def posts():
    out = []
    for p in sorted((ROOT / 'content/posts').glob('*.md')):
        if p.name == '_index.md':
            continue
        text = p.read_text(encoding='utf-8').replace('\r\n', '\n')
        fm, body = split_front_matter(text)
        if fm.startswith('+++'):
            meta = tomllib.loads(fm.strip().strip('+').strip())
        else:
            meta = _parse_yaml(fm)
        out.append(Post(p, p.stem, meta, body))
    return out


class Node:
    def __init__(self, tag, attrs):
        self.tag = tag
        self.attrs = dict(attrs)
        self.children = []
        self._text = []

    @property
    def text(self):
        return ' '.join(' '.join(self._all_text()).split())

    def _all_text(self):
        for item in self._text:
            yield item.text if isinstance(item, Node) else item

    @property
    def classes(self):
        return (self.attrs.get('class') or '').split()


VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
        'link', 'meta', 'source', 'track', 'wbr'}


class Html(HTMLParser):
    def __init__(self, raw):
        super().__init__(convert_charrefs=True)
        self.raw = raw
        self.root = Node('root', [])
        self.nodes = []
        self._stack = [self.root]
        self.feed(raw)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        parent = self._stack[-1]
        parent.children.append(node)
        parent._text.append(node)
        self.nodes.append(node)
        if tag not in VOID:
            self._stack.append(node)

    def handle_endtag(self, tag):
        for i in range(len(self._stack) - 1, 0, -1):
            if self._stack[i].tag == tag:
                del self._stack[i:]
                break

    def handle_data(self, data):
        self._stack[-1]._text.append(data)

    def select(self, tag, cls=None):
        return [n for n in self.nodes
                if n.tag == tag and (cls is None or cls in n.classes)]


def page(rel):
    path = BUILD / rel
    assert path.exists(), f'构建产物不存在：{rel}'
    return Html(path.read_text(encoding='utf-8'))
