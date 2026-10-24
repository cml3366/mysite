"""构建产物断言：先以 hugo --minify --buildFuture -d .build 构建一次，再检查输出。"""
import re
import shutil
import subprocess
import unittest
import urllib.parse

from helpers import BUILD, EXPECTED, ROOT, page, posts


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


def published():
    return [p for p in posts() if not p.meta.get('draft')]


def href_to_file(href):
    """把页面里的相对或绝对链接换算成 .build 下的 index.html。"""
    rel = urllib.parse.unquote(urllib.parse.urlparse(href).path)
    rel = rel.removeprefix('https://blog.cml3366.cn').lstrip('./').lstrip('/')
    return BUILD / rel / 'index.html'


class TestHome(unittest.TestCase):
    def setUp(self):
        self.h = page('index.html')

    def test_hero(self):
        t = ' '.join(n.text for n in self.h.select('section', 'sk-hero'))
        self.assertIn('宇宙之光 × 古典之韵', t)
        self.assertIn('从古典智慧到量子科学', t)

    def test_six_topic_cards_in_order(self):
        cards = self.h.select('a', 'sk-topic')
        self.assertEqual([c.text.split()[0] for c in cards], list(EXPECTED))
        self.assertIn('11 篇', cards[1].text)

    def test_topic_links_resolve(self):
        for c in self.h.select('a', 'sk-topic'):
            self.assertTrue(href_to_file(c.attrs['href']).exists(), c.attrs['href'])

    def test_ten_recent_rows(self):
        self.assertEqual(len(self.h.select('a', 'sk-row')), 10)

    def test_recent_includes_newest_by_date(self):
        newest = max(published(), key=lambda p: str(p.meta['date']))
        self.assertIn(newest.meta['title'], self.h.select('a', 'sk-row')[0].text)

    def test_more_link(self):
        self.assertTrue(f'查看全部 {len(published())} 篇' in self.h.raw)

    def test_menu(self):
        labels = [a.text for nav in self.h.select('nav') for a in nav.children if a.tag == 'a'] \
            or [a.text for a in self.h.select('a')]
        for label in ('文章', '专题', 'RSS'):
            self.assertIn(label, labels)


def post_page(p):
    return page(f"posts/{p.meta.get('slug', p.slug)}/index.html")


def post(stem):
    return post_page(next(p for p in posts() if p.slug == stem))


def related_rows(h):
    return [n for a in h.select('aside', 'sk-related') for n in a.children if 'sk-row' in n.classes]


class TestArticle(unittest.TestCase):
    def test_title_meta_present(self):
        h = post('qidao')
        self.assertIn('炁道：第九卦的创立与三态易学体系的开启', h.select('h1')[0].text)
        self.assertTrue(h.select('time') or '分钟' in h.raw)

    def test_duplicate_body_h1_marked(self):
        self.assertEqual(len(post('qidao').select('h1', 'sk-dup-title')), 1)

    def test_quote_first_article_keeps_quote(self):
        h = post('superconducting-qutrit')
        self.assertTrue(h.select('blockquote'))
        self.assertEqual(len(h.select('h1', 'sk-dup-title')), 1)

    def test_body_without_h1_has_no_dup_mark(self):
        h = post('weitegensitan-zhexue-yanjiu-liubian-buju')
        self.assertEqual(h.select('h1', 'sk-dup-title'), [])

    def test_toc_only_with_three_h2(self):
        for p in published():
            n = sum(1 for line in p.body.splitlines() if line.startswith('## '))
            self.assertEqual(bool(post_page(p).select('div', 'toc')), n >= 3, p.slug)

    def test_related_excludes_self_and_caps_at_three(self):
        rows = related_rows(post('weilai-fu-gaowei-xiaoyaoyou'))
        self.assertEqual(len(rows), 2)
        self.assertNotIn('未来赋', ' '.join(r.text for r in rows))
        self.assertEqual(len(related_rows(post('qidao'))), 3)

    def test_share_and_pagination(self):
        h = post('qidao')
        self.assertTrue(h.select('div', 'post-share'))
        self.assertTrue(h.select('nav', 'sk-pagination'))

    def test_article_wrapped(self):
        self.assertTrue(post('qidao').select('div', 'sk-article'))


class TestTypography(unittest.TestCase):
    def test_hero_title_breaks_only_at_times_sign(self):
        parts = [s.text for s in page('index.html').select('span', 'sk-nowrap')]
        self.assertEqual(parts[:2], ['宇宙之光', '古典之韵'])

    def test_article_meta_in_chinese(self):
        h = post('qidao')
        head = next(n for n in h.nodes if n.attrs.get('id') == 'single_header').text
        self.assertIn('2025年11月19日', head)
        self.assertNotIn('words', head)


class TestLists(unittest.TestCase):
    def test_posts_lists_all(self):
        self.assertEqual(len(page('posts/index.html').select('a', 'sk-row')), len(published()))

    def test_category_page(self):
        h = page('categories/新易体系/index.html')
        self.assertEqual(len(h.select('a', 'sk-row')), 10)
        self.assertIn('九卦炁与三态易学的创立、方法与预测', h.select('p', 'sk-topic-desc')[0].text)

    def test_terms_page_cards(self):
        self.assertEqual(len(page('categories/index.html').select('a', 'sk-topic')), 6)

    def test_no_replacement_char_in_build(self):
        bad = [str(p.relative_to(BUILD)) for p in BUILD.rglob('*.html')
               if '�' in p.read_text(encoding='utf-8')]
        self.assertEqual(bad, [])


if __name__ == '__main__':
    unittest.main()
