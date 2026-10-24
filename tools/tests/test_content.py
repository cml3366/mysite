"""内容层断言：编码、锁定配置。"""
import tomllib
import unittest
from collections import Counter

from helpers import EXPECTED, ROOT, posts


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


class TestTopics(unittest.TestCase):
    def test_topics_file_order(self):
        t = tomllib.loads((ROOT / 'data/topics.toml').read_text(encoding='utf-8'))['topic']
        self.assertEqual([x['name'] for x in t], list(EXPECTED))
        self.assertEqual(t[0]['desc'], '九卦炁与三态易学的创立、方法与预测')

    def test_every_published_post_has_one_known_category(self):
        for p in posts():
            if p.meta.get('draft'):
                continue
            self.assertEqual(len(p.meta.get('categories', [])), 1, p.slug)
            self.assertIn(p.meta['categories'][0], EXPECTED, p.slug)

    def test_category_counts(self):
        c = Counter(p.meta['categories'][0] for p in posts() if not p.meta.get('draft'))
        self.assertEqual(dict(c), EXPECTED)

    def test_placeholders_are_drafts(self):
        d = {p.slug: p.meta.get('draft') for p in posts()}
        self.assertIs(d['first'], True)
        self.assertIs(d['hello-world'], True)

    def test_spot_check_assignments(self):
        m = {p.slug: p.meta.get('categories', [None])[0] for p in posts()}
        self.assertEqual(m['uploaded-article'], '新易体系')
        self.assertEqual(m['qigua-tianyan'], '古典研究')
        self.assertEqual(m['bashi-yi-gua-qigua-yunsuan-quantum-entanglement'], '量子与易学')
        self.assertEqual(m['dongfang-zhexue-xiandai-wuli'], '哲思与赋')


if __name__ == '__main__':
    unittest.main()
