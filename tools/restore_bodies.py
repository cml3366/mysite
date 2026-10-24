"""一次性脚本：用 9d9dac8 之前的完好正文恢复被写坏的文章，front matter 保留当前版本。

用法：python -I tools/restore_bodies.py [--check]
"""
import difflib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'tests'))
from helpers import split_front_matter  # noqa: E402

CLEAN = {
    'badao-jiugua-san-tai-yongxian.md': 'e3ca6a3',
    'binary-ternary-quantum.md': '922a23f',
    'dongfang-zhexue-xiandai-wuli.md': '8f6c0a9',
    'erqian-liuyao.md': 'cd921bd',
    'hetu-luoshu-quantum-entanglement.md': '340d2db',
    'huangdi-neijing-taisu-research-postscript.md': '23d1e69',
    'physics-quantum-jiugua-qi.md': 'a8a1b05',
    'qi-neiwaijing-sanyuan.md': '3e31b54',
    'qidao.md': '23d1e69',
    'qigua-tianyan.md': '23d1e69',
    'quantum-computing-jiugua-qi.md': '950797e',
    'quantum-entanglement-mingli.md': 'f6e504d',
    'quantum-jiugua-qi.md': 'a3bd58e',
    'quantum-yixue-system-framework.md': '7e1f654',
    'xin-yi-quantum.md': '5c1f0ff',
    'xinyi-preface.md': 'a9da339',
    'zhengzong-yuce.md': '740e893',
}


def git_show(commit, name):
    out = subprocess.run(['git', 'show', f'{commit}:content/posts/{name}'],
                         cwd=ROOT, capture_output=True, check=True).stdout
    return out.decode('utf-8').replace('\r\n', '\n')


def _norm(text):
    return re.sub(r'\n{3,}', '\n\n', text.strip())


def corruption_pattern(cur_body):
    """把当前正文转成正则：每段连续的 �/? 是通配符（坏字常连带吞掉其后的 *、数字、换行），其余逐字匹配。"""
    parts = []
    for chunk in re.split(r'([�?]+)', _norm(cur_body)):
        if not chunk:
            continue
        if set(chunk) <= {'�', '?'}:
            parts.append(f'[\\s\\S]{{1,{3 * len(chunk)}}}?')
        else:
            parts.append(re.escape(chunk))
    return re.compile(''.join(parts))


def mismatches(old_body, cur_body):
    """完好正文与当前正文除乱码处外不一致时，返回首个分歧点的上下文。"""
    old = _norm(old_body)
    if corruption_pattern(cur_body).fullmatch(old):
        return []
    sm = difflib.SequenceMatcher(None, old, _norm(cur_body), autojunk=False)
    bad = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op != 'equal' and not set(_norm(cur_body)[j1:j2]) <= {'�', '?'}:
            bad.append((old[max(0, i1 - 20):i2 + 20], _norm(cur_body)[max(0, j1 - 20):j2 + 20]))
    return bad or [('（通配匹配失败）', '')]


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    check_only = '--check' in sys.argv
    restored, skipped = [], []
    for name, commit in CLEAN.items():
        path = ROOT / 'content/posts' / name
        cur = path.read_bytes().decode('utf-8', 'replace').replace('\r\n', '\n')
        cur_fm, cur_body = split_front_matter(cur)
        _, old_body = split_front_matter(git_show(commit, name))
        bad = mismatches(old_body, cur_body)
        if bad:
            skipped.append(name)
            print(f'[不一致] {name}：{len(bad)} 处')
            for old, now in bad[:3]:
                print(f'    完好：{old!r}\n    当前：{now!r}')
            continue
        restored.append(name)
        print(f'[通过] {name}')
        if not check_only:
            with open(path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(cur_fm + old_body)
    verb = '可恢复' if check_only else '恢复'
    print(f'{verb} {len(restored)} 篇，跳过 {len(skipped)} 篇：{skipped}')


if __name__ == '__main__':
    main()
