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

    def test_light_mode_blue_and_outline_button_contrast(self):
        c = css()
        self.assertTrue(re.search(r'html:not\(\.dark\)\{[^}]*--sk-blue:rgb\(var\(--color-secondary-700\)\)', c),
                        '浅色模式缺少 --sk-blue 覆盖')
        self.assertTrue(re.search(r'html:not\(\.dark\) \.sk-btn\{[^}]*--color-primary-800', c),
                        '浅色模式描边按钮未加深')

    def test_serif_stack_latin_first(self):
        # 宋体自带的西文是等宽字形，英文需先落到 Georgia
        self.assertTrue(re.search(r'--sk-serif:Georgia,', css()), '标题字体栈未以西文衬线体开头')

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

    def test_distinct_body_titles_stay_visible(self):
        # 正文 h1 与页面标题不同（英文论文名、另一副题），不能隐藏
        for stem in ('badao-jiugua-san-tai-yongxian', 'qigua-tianyan'):
            self.assertEqual(post(stem).select('h1', 'sk-dup-title'), [], stem)

    def test_bracketed_same_title_is_hidden(self):
        # 《前知》与标题「前知」只差书名号，属重复
        self.assertEqual(len(post('uploaded-article').select('h1', 'sk-dup-title')), 1)
        # 「意识/灵魂…」与「意识与灵魂…」只差一字，也属重复
        self.assertEqual(len(post('consciousness-quantum-xinyi').select('h1', 'sk-dup-title')), 1)

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


class TestSingleLanguage(unittest.TestCase):
    def test_no_language_subsites(self):
        self.assertEqual([d for d in ('en', 'zh-cn') if (BUILD / d).exists()], [])

    def test_html_lang_zh_cn(self):
        self.assertEqual(page('index.html').select('html')[0].attrs.get('lang'), 'zh-cn')


class TestLists(unittest.TestCase):
    def test_posts_lists_all(self):
        self.assertEqual(len(page('posts/index.html').select('a', 'sk-row')), len(published()))

    def test_category_page(self):
        h = page('categories/新易体系/index.html')
        self.assertEqual(len(h.select('a', 'sk-row')), 10)
        self.assertIn('九卦炁与三态易学的创立、方法与预测', h.select('p', 'sk-topic-desc')[0].text)

    def test_tag_pages_keep_theme_template(self):
        self.assertTrue((BUILD / 'tags/qutrit/page/1/index.html').exists())
        self.assertEqual(page('tags/qutrit/index.html').select('p', 'sk-list-count'), [])

    def test_tags_overview_not_topic_cards(self):
        self.assertEqual(page('tags/index.html').select('a', 'sk-topic'), [])

    def test_terms_page_cards(self):
        self.assertEqual(len(page('categories/index.html').select('a', 'sk-topic')), 6)

    def test_no_replacement_char_in_build(self):
        bad = [str(p.relative_to(BUILD)) for p in BUILD.rglob('*.html')
               if '�' in p.read_text(encoding='utf-8')]
        self.assertEqual(bad, [])


SHARE_TARGETS = ['wechat', 'weibo', 'qzone', 'zhihu', 'x', 'facebook', 'telegram', 'copy', 'rss']
SHARE_PAGES = ['index.html', 'posts/index.html', 'categories/index.html', 'tags/qutrit/index.html']


def share_targets(node):
    return [n.attrs.get('data-share') for n in node.children if n.attrs.get('data-share')] + \
        [t for c in node.children for t in share_targets(c)]


class TestShare(unittest.TestCase):
    def test_brand_icons_installed(self):
        for name in ('wechat', 'sinaweibo', 'qq', 'zhihu'):
            svg = (ROOT / f'assets/icons/{name}.svg').read_text(encoding='utf-8')
            self.assertIn('fill="currentColor"', svg, name)
            self.assertNotIn('<script', svg, name)

    def test_header_share_buttons_on_every_kind_of_page(self):
        for rel in SHARE_PAGES + ['posts/qidao-jiugua-san-tai-yixue/index.html']:
            ids = [n.attrs.get('id') for n in page(rel).select('button')]
            self.assertIn('share-button', ids, rel)
            self.assertIn('share-button-mobile', ids, rel)

    def test_footer_share_row_has_all_targets(self):
        for rel in SHARE_PAGES:
            rows = [n for n in page(rel).select('div', 'sk-share') if 'sk-share-footer' in n.classes]
            self.assertEqual(len(rows), 1, rel)
            self.assertEqual(share_targets(rows[0]), SHARE_TARGETS, rel)

    def test_footer_share_row_is_inside_footer(self):
        footer = page('index.html').select('footer')[0]
        self.assertIn('sk-share-footer', ' '.join(' '.join(n.classes) for n in self._walk(footer)))

    def _walk(self, node):
        yield node
        for c in node.children:
            yield from self._walk(c)

    def test_article_end_uses_icon_row(self):
        h = post('qidao')
        ends = [n for n in h.select('div', 'sk-share') if 'sk-share-article' in n.classes]
        self.assertEqual(len(ends), 1)
        self.assertEqual(share_targets(ends[0]), SHARE_TARGETS)
        self.assertFalse('btn-share' in h.raw, '旧的文字分享按钮仍在')

    def test_single_modal_and_unique_ids(self):
        for rel in ['index.html', 'posts/qidao-jiugua-san-tai-yixue/index.html']:
            h = page(rel)
            self.assertEqual(len([n for n in h.nodes if n.attrs.get('id') == 'sk-share-modal']), 1, rel)
            # 主题目录组件本身会输出两份 TableOfContents，这里只查分享相关的 id
            ids = [n.attrs['id'] for n in h.nodes if 'share' in (n.attrs.get('id') or '')]
            self.assertEqual([i for i in set(ids) if ids.count(i) > 1], [], rel)

    def test_modal_class_used_only_by_dialog_container(self):
        # 弹窗里那一排图标不能沿用弹窗容器的类名，否则会被一起定位到屏幕中央
        h = page('index.html')
        self.assertEqual([n.attrs.get('id') for n in h.nodes if 'sk-share-modal' in n.classes], ['sk-share-modal'])

    def test_share_script_loaded_with_integrity(self):
        scripts = [n for n in page('index.html').select('script') if 'share' in (n.attrs.get('src') or '')]
        self.assertEqual(len(scripts), 1)
        self.assertTrue(scripts[0].attrs.get('integrity'))


if __name__ == '__main__':
    unittest.main()
