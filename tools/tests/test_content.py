"""内容层断言：编码、锁定配置。"""
import tomllib
import unittest

from helpers import ROOT, posts


class TestEncoding(unittest.TestCase):
    def test_no_replacement_char_in_posts(self):
        bad = [p.slug for p in posts() if '�' in p.path.read_text(encoding='utf-8')]
        self.assertEqual(bad, [])

    def test_no_bom(self):
        bad = [p.slug for p in posts() if p.path.read_bytes().startswith(b'\xef\xbb\xbf')]
        self.assertEqual(bad, [])


class TestLockedConfig(unittest.TestCase):
    def test_hugo_toml_locks(self):
        cfg = tomllib.loads((ROOT / 'hugo.toml').read_text(encoding='utf-8'))
        self.assertIs(cfg['buildFuture'], True)
        self.assertEqual(cfg['pagination']['pagerSize'], 50)

    def test_workflow_build_future(self):
        self.assertIn('--buildFuture',
                      (ROOT / '.github/workflows/deploy.yml').read_text(encoding='utf-8'))

    def test_list_paginate_50(self):
        self.assertIn('.Paginate (.Pages.ByDate.Reverse) 50',
                      (ROOT / 'layouts/_default/list.html').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
