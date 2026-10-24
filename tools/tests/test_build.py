"""构建产物断言：先以 hugo --minify --buildFuture -d .build 构建一次，再检查输出。"""
import re
import shutil
import subprocess
import unittest

from helpers import BUILD, ROOT, page


def setUpModule():
    shutil.rmtree(BUILD, ignore_errors=True)
    r = subprocess.run(['hugo', '--minify', '--buildFuture', '-d', str(BUILD)],
                       cwd=ROOT, capture_output=True)
    if r.returncode != 0:
        raise AssertionError('hugo 构建失败：\n' + r.stderr.decode('utf-8', 'replace'))


def css():
    return '\n'.join(p.read_text(encoding='utf-8') for p in (BUILD / 'css').glob('*.css'))


class TestStyles(unittest.TestCase):
    # 构建产物很大，断言只比较布尔值，避免失败时把整页打印出来
    def test_scheme_applied(self):
        self.assertTrue('--color-neutral-800:10,15,31' in css().replace(' ', ''), '深空底色未生效')

    def test_no_reader_css(self):
        self.assertFalse('reader.css' in page('index.html').raw, '页面仍引用 reader.css')
        self.assertFalse((BUILD / 'css/reader.css').exists())

    def test_no_webfont(self):
        raw = page('index.html').raw
        self.assertFalse('fonts.googleapis' in raw or 'fonts.gstatic' in raw, '加载了网络字体')

    def test_light_mode_uses_dark_gold(self):
        self.assertTrue(re.search(r'html:not\(\.dark\)[^{]*\.sk-', css()), '缺少浅色模式覆盖')


if __name__ == '__main__':
    unittest.main()
