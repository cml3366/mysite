# 深空星图改版 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复 17 篇文章的正文乱码，并把 blog.cml3366.cn 改版为「深空星图」风格，包括专题首页、统一的文章页和列表页。

**Architecture:** 不改 Blowfish 源码。所有改动都放在项目根目录的覆盖层：`assets/css/schemes/shenkong.css` 和 `assets/css/custom.css` 负责配色与排版，`layouts/` 下的模板负责结构，`data/topics.toml` 是专题的唯一数据源。验证使用 Python 标准库 `unittest`：构建产物输出到 `.build/`（不进 git），测试对构建产物做断言。

**Tech Stack:** Hugo 0.152.2 extended、Blowfish v2.91.0（git submodule）、Tailwind 类（主题自带）、Python 3 标准库（`unittest`、`html.parser`、`difflib`、`tomllib`）。

**Spec:** `docs/superpowers/specs/2026-10-24-blog-redesign-design.md`

## Global Constraints

- 以下锁定项不得改动：`hugo.toml` 中的 `buildFuture = true`，`[pagination] pagerSize = 50`；`.github/workflows/deploy.yml` 中的 `--buildFuture`；`layouts/_default/list.html` 中的 `.Paginate (.Pages.ByDate.Reverse) 50`。
- 不改 `themes/blowfish/` 下的任何文件。
- 不加载网络字体。标题字体栈：`"Songti SC", "Noto Serif CJK SC", "Source Han Serif SC", SimSun, serif`；正文字体栈：`"PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif`。
- 颜色：底色 `#0a0f1f`，正文 `#e8e6df`，次要文字 `#a3a7b8`，主色 `#f3d58b`，主色悬停 `#c9a34e`，辅色 `#7d97d6`，主视觉渐变起点 `#1b2a52`。
- 文章正文 17px，行高 1.85，`max-width: 40rem`。
- 所有 `.md`、`.html`、`.toml`、`.css`、`.py` 文件一律 UTF-8 无 BOM、LF 换行。写文件时用编辑工具或 Python 的 `open(..., 'w', encoding='utf-8', newline='\n')`。**不要用 PowerShell 的 `Set-Content` 或 `Out-File`**，这正是乱码的来源。
- 构建命令统一为：`hugo --minify --buildFuture -d .build`。不要构建到 `public/`，那里是已提交的旧产物，不在本次范围。
- 提交信息用中文，末尾加 `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`。
- 只在分支 `redesign/shenkong` 上提交，不推送。
- 只 `git add` 本计划列出的文件。工作区里还有大量与本次无关的未提交改动（`public/`、`asset_*.py`、各种说明文档等），不得带进提交。

## Review Focus

1. **正文开头不是 `# 标题` 的文章**：比如 `superconducting-qutrit.md` 开头是引用块，第二个元素才是 `# 标题`。隐藏规则只能隐藏与页面标题重复的那一个 `h1`，引用块必须照常显示。对应 Task 5 的 `test_quote_first_article_keeps_quote`。
2. **未来日期的文章**：首页最新列表、`/posts/` 和专题页都必须包含日期晚于构建当天的文章。对应 Task 4 的 `test_recent_includes_newest_by_date`：它按 front matter 日期取最新的那篇，断言它出现在首页。
3. **中文专题链接**：首页卡片的 `href` 必须指向 `.build/categories/<专题名>/index.html` 实际存在的目录，不能因为转码不一致出现 404。对应 Task 4 的 `test_topic_links_resolve`。
4. **同专题文章不足 3 篇**：「哲思与赋」只有 3 篇，每篇只能推荐另外 2 篇。推荐列表不能包含本文，也不能报错。对应 Task 5 的 `test_related_excludes_self_and_caps_at_three`。
5. **浅色模式的对比度**：主色 `#f3d58b` 在米白底上几乎看不清，浅色模式下标题和链接必须改用 primary-700。对应 Task 3 的 `test_light_mode_uses_dark_gold`，以及 Task 7 的人工检查。

---

## 文件结构

| 文件 | 职责 |
|---|---|
| `tools/restore_bodies.py` | 一次性脚本：按表恢复 17 篇文章的正文，并在恢复前校验 |
| `tools/tests/helpers.py` | 测试公用工具：读取构建产物、解析 HTML、读取文章 front matter |
| `tools/tests/test_content.py` | 内容层断言：无乱码、分类、草稿、锁定配置 |
| `tools/tests/test_build.py` | 构建产物断言：首页、文章页、列表页、样式 |
| `data/topics.toml` | 六个专题的顺序、名称和说明 |
| `assets/css/schemes/shenkong.css` | Blowfish 配色色阶 |
| `assets/css/custom.css` | 字体、背景、卡片、文章排版、浅色模式修正 |
| `layouts/partials/home/custom.html` | 首页：主视觉、专题卡片、最新列表 |
| `layouts/partials/topic-cards.html` | 六张专题卡片，首页和 `/categories/` 共用 |
| `layouts/partials/post-row.html` | 单行文章条目，首页、`/posts/` 和专题页共用 |
| `layouts/partials/related-topic.html` | 同专题文章推荐 |
| `layouts/_default/single.html` | 文章页 |
| `layouts/_default/list.html` | 列表页，只改展示部分 |
| `layouts/_default/terms.html` | `/categories/` 总览页 |

---

### Task 1: 测试骨架与正文乱码恢复

**Files:**
- Create: `tools/tests/helpers.py`
- Create: `tools/tests/test_content.py`
- Create: `tools/restore_bodies.py`
- Modify: 17 篇 `content/posts/*.md`，名单见设计文档第 3.1 节
- Modify: `.git/info/exclude`，追加 `.build/` 和 `.build-server/`

**Interfaces:**
- Produces:
  - `helpers.ROOT: pathlib.Path`：项目根目录，即 `tools/tests` 往上两级
  - `helpers.BUILD: pathlib.Path`：`ROOT / '.build'`
  - `helpers.posts() -> list[Post]`：遍历 `content/posts/*.md`，跳过 `_index.md`
  - `Post`：一个 dataclass，字段为 `path: Path`、`slug: str`（文件名去掉 `.md`）、`meta: dict`（用 `tomllib` 解析 `+++` 包围的 front matter；遇到 `---` 包围的 YAML 时，只解析 `key: "value"` 这种简单格式）、`body: str`
  - `helpers.split_front_matter(text: str) -> tuple[str, str]`：返回 `(front_matter_含分隔线, body)`
  - `helpers.page(rel: str) -> Html`：读取 `BUILD / rel`，`rel` 可以是 `'index.html'` 或 `'posts/qidao/index.html'`；文件不存在时抛出 `AssertionError`
  - `Html`：基于 `html.parser` 的轻量解析结果，提供 `select(tag: str, cls: str | None = None) -> list[Node]`。`Node` 有 `attrs: dict`、`text: str`（拼接后的纯文本）和 `children: list[Node]`

- [ ] **Step 1: 写失败的测试**

`tools/tests/test_content.py`：

```python
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
        self.assertIn('--buildFuture', (ROOT / '.github/workflows/deploy.yml').read_text(encoding='utf-8'))

    def test_list_paginate_50(self):
        self.assertIn('.Paginate (.Pages.ByDate.Reverse) 50', (ROOT / 'layouts/_default/list.html').read_text(encoding='utf-8'))
```

- [ ] **Step 2: 运行，确认失败**

Run: `python -m unittest discover -s tools/tests -v`
Expected: `test_no_replacement_char_in_posts` FAIL，列出 17 个 slug；其余测试 PASS。

- [ ] **Step 3: 实现 `tools/restore_bodies.py`**

脚本内置一个字典 `CLEAN = {文件名: 提交号}`，内容照抄设计文档第 3.1 节的表。命令行参数 `--check` 表示只校验、不写文件；不带参数时，校验通过的文件会被写回。

对每个文件执行以下步骤：

1. `cur = 当前文件内容`；`old = git show <提交号>:content/posts/<文件名>`，按 UTF-8 解码。两者都先把 CRLF 统一成 LF。
2. 分别用 `split_front_matter` 拆开，得到 `cur_fm, cur_body` 和 `_, old_body`。
3. **校验**：对 `old_body` 和 `cur_body` 做 `difflib.SequenceMatcher(None, old_body, cur_body, autojunk=False).get_opcodes()`。每个不是 `equal` 的片段都必须同时满足下面三条：
   - 当前版本一侧只包含 `�` 和 `?`；
   - 当前版本一侧非空；
   - 完好版本一侧的长度不超过 4 个字符，并且不含换行。

   任何一个片段不满足，这篇文章就判为「不一致」，打印前 3 处差异的上下文（前后各 20 个字符），然后跳过不写。
4. 校验通过后写入 `cur_fm + old_body`，编码 UTF-8 无 BOM，换行 LF。
5. 最后打印汇总：`恢复 N 篇，跳过 M 篇：<名单>`。

- [ ] **Step 4: 先只校验**

Run: `python -I tools/restore_bodies.py --check`
Expected: 打印 17 篇文章的校验结果。**如果有文章被判为「不一致」，就停在这里**，把它的差异上下文报告给作者，等作者决定后再继续。

- [ ] **Step 5: 写入恢复结果**

Run: `python -I tools/restore_bodies.py`
Expected: `恢复 17 篇，跳过 0 篇`。

- [ ] **Step 6: 运行测试，确认通过**

Run: `python -m unittest discover -s tools/tests -v`
Expected: 全部 PASS。

- [ ] **Step 7: 抽查恢复结果**

Run: `git diff --stat -- content/posts`，然后看 `qidao.md` 的 diff。
Expected: front matter 没有变化；正文里的 `�?` 都变回了完整的汉字，比如标题恢复成「……体系的开启」。

- [ ] **Step 8: 提交**

```bash
git add tools/restore_bodies.py tools/tests/helpers.py tools/tests/test_content.py content/posts/<17 篇文章>
git commit -m "fix: 恢复 9d9dac8 写坏的 17 篇文章正文"
```

---

### Task 2: 专题数据、分类和草稿

**Files:**
- Create: `data/topics.toml`
- Modify: 42 篇 `content/posts/*.md` 的 front matter，以及 `first.md`、`hello-world.md`
- Modify: `tools/tests/test_content.py`

**Interfaces:**
- Produces: `data/topics.toml` 的结构如下。模板中通过 `site.Data.topics.topic` 读取，按数组顺序遍历。

```toml
[[topic]]
name = '新易体系'
desc = '九卦炁与三态易学的创立、方法与预测'
# 其余五个专题按设计文档第 5.2 节的顺序和文字照抄
```

- [ ] **Step 1: 写失败的测试**

```python
EXPECTED = {'新易体系': 10, '量子与易学': 11, '三进制与九卦': 8, '古典研究': 5, '科学前沿': 5, '哲思与赋': 3}

class TestTopics(unittest.TestCase):
    def test_topics_file_order(self):
        t = tomllib.loads((ROOT / 'data/topics.toml').read_text(encoding='utf-8'))['topic']
        self.assertEqual([x['name'] for x in t], list(EXPECTED))
        self.assertEqual(t[0]['desc'], '九卦炁与三态易学的创立、方法与预测')

    def test_every_published_post_has_one_known_category(self):
        pub = [p for p in posts() if not p.meta.get('draft')]
        for p in pub:
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
```

- [ ] **Step 2: 运行，确认失败**

Run: `python -m unittest tools.tests.test_content -v`（如果包导入方式不通，就改用 `discover`）
Expected: 新增的 5 个测试 FAIL。

- [ ] **Step 3: 写 `data/topics.toml`，并给每篇文章加分类**

- 每篇文章在 front matter 的 `tags` 那一行后面插入 `categories = ['<专题名>']`。归类照抄设计文档第 6 节。
- `first.md` 和 `hello-world.md` 中的 `draft` 改为 `true`。
- front matter 是 YAML 格式（`---` 包围）的文章，改用 `categories: ["<专题名>"]`。
- 可以用一次性的 Python 片段批量插入，不需要保留成文件。插入时只动这一行，正文一个字节都不许变。

- [ ] **Step 4: 运行测试，确认通过**

Run: `python -m unittest discover -s tools/tests -v`
Expected: 全部 PASS。

- [ ] **Step 5: 提交**

```bash
git add data/topics.toml content/posts/*.md tools/tests/test_content.py
git commit -m "feat: 文章归入六个专题，占位稿改为草稿"
```

提交前先运行 `git diff --cached --stat`，确认 `content/posts` 下的每个文件只改了 1–2 行。

---

### Task 3: 配色与全局样式

**Files:**
- Create: `assets/css/schemes/shenkong.css`
- Create: `assets/css/custom.css`
- Create: `tools/tests/test_build.py`
- Modify: `hugo.toml`：把 `colorScheme = 'dark'` 改为 `'shenkong'`，删除 `customCSS` 这一行
- Delete: `static/css/reader.css`

**Interfaces:**
- Produces，后续 Task 4 至 Task 6 会用到以下 CSS 类名：
  - `.sk-serif`：标题字体栈，加 `letter-spacing: .08em`
  - `.sk-card`：卡片样式，背景 `rgba(255,255,255,.05)`，边框 `1px solid rgba(243,213,139,.25)`，圆角 `.75rem`
  - `.sk-hero`：首页主视觉的背景，包括径向渐变、星点和九宫纹路
  - `.sk-row`：单行文章条目，悬停时背景变为 `rgba(243,213,139,.06)`
  - `.sk-tag`：专题小标签
  - `.sk-article`：加在文章页 `.article-content` 外层，负责正文排版
- Produces，`test_build.py` 的类级准备：`setUpModule()` 只执行一次 `hugo --minify --buildFuture -d .build`。返回码不为 0 时直接失败，失败信息附上 stderr。

- [ ] **Step 1: 写失败的测试**

```python
class TestStyles(unittest.TestCase):
    def css(self):
        # 读取 .build 下所有 css/*.css 文件（主题会把 scheme 和 custom 打包进带指纹的文件名）
        ...
    def test_scheme_applied(self):
        self.assertIn('10,15,31', self.css().replace(' ', ''))   # #0a0f1f 写成 RGB 三元组
    def test_no_reader_css(self):
        self.assertNotIn('reader.css', page('index.html').raw)
        self.assertFalse((BUILD / 'css/reader.css').exists())
    def test_no_webfont(self):
        raw = page('index.html').raw
        self.assertNotIn('fonts.googleapis', raw)
        self.assertNotIn('fonts.gstatic', raw)
    def test_light_mode_uses_dark_gold(self):
        self.assertRegex(self.css(), r'html:not\(\.dark\)[^{]*\.sk-')   # 浅色模式下 sk-* 类有单独覆盖
```

`Html` 对象需要增加 `raw: str` 属性，保存原始 HTML。这一改动在 Task 3 中补进 `helpers.py`。

- [ ] **Step 2: 运行，确认失败**

Run: `python -m unittest tools.tests.test_build -v`
Expected: `test_scheme_applied`、`test_no_reader_css`、`test_light_mode_uses_dark_gold` FAIL。

- [ ] **Step 3: 写 `shenkong.css`**

格式与 `themes/blowfish/assets/css/schemes/ocean.css` 相同：在 `:root` 下定义 `--color-neutral`、`--color-neutral-50` 至 `-950`、`--color-primary-50` 至 `-950`、`--color-secondary-50` 至 `-950`，值都是 `R, G, B` 形式的三元组。以下几级的值必须准确：

| 变量 | 值 |
|---|---|
| neutral-50 | `250, 247, 240` |
| neutral-100 | `232, 230, 223` |
| neutral-400 | `163, 167, 184` |
| neutral-800 | `17, 24, 46` |
| neutral-900 | `10, 15, 31` |
| primary-300 | `243, 213, 139` |
| primary-500 | `201, 163, 78` |
| primary-700 | `138, 106, 36` |
| secondary-400 | `125, 151, 214` |

其余各级在相邻两级之间插值，保持单调。

- [ ] **Step 4: 写 `custom.css`**

- 定义上面列出的 `.sk-*` 类。
- `body` 使用正文字体栈；`h1, h2, h3, .sk-serif` 使用标题字体栈。
- `.dark body` 加 `background-image: linear-gradient(180deg, rgba(27,42,82,.35), transparent 320px)`，即页顶的淡渐变。
- `.sk-hero` 背景按以下顺序叠加：
  - 4 至 6 个 `radial-gradient(1px 1px at x% y%, …)` 画星点，其中一颗用 `#ffd98a`，大小 1.5px；
  - 一层九宫纹路：`repeating-linear-gradient` 横竖各一层，透明度 ≤ .05；
  - 最底层是 `radial-gradient(ellipse at 70% 0%, #1b2a52, #0a0f1f 60%)`。
- `.sk-article` 文章排版：
  - 正文 `font-size: 17px; line-height: 1.85; max-width: 40rem`；
  - `h2::before { content: '◆'; color: rgb(var(--color-primary-300)); font-size: .7em; margin-right: .5em; vertical-align: .15em }`；
  - `blockquote` 左边线 `3px solid #7d97d6`，背景 `rgba(125,151,214,.08)`；
  - `pre` 使用 `.sk-card` 的底色，圆角 `.6rem`；
  - `table` 的 `th` 文字颜色用 primary-300；
  - `img` 居中，`border-radius: .6rem`。
- 浅色模式覆盖（`html:not(.dark)` 前缀）：`.sk-hero` 改为浅色渐变 `#f5f0e6` 到 `#ebe3d0`，星点改为 primary-700 并降低透明度；`.sk-card` 边框改为 `rgba(138,106,36,.25)`；`h2::before`、链接和标题改用 primary-700。

- [ ] **Step 5: 修改 `hugo.toml`，删除 `static/css/reader.css`**

只改 `colorScheme`、删除 `customCSS` 这一行。不要碰其他行，锁定项的测试会兜底检查。

- [ ] **Step 6: 运行测试，确认通过**

Run: `python -m unittest discover -s tools/tests -v`
Expected: 全部 PASS。

- [ ] **Step 7: 提交**

```bash
git add assets/css hugo.toml tools/tests/test_build.py tools/tests/helpers.py
git rm static/css/reader.css
git commit -m "feat: 深空星图配色与全局排版，移除 reader.css"
```

注意：`hugo.toml` 在工作区里可能已经有别的未提交改动。如果 `git diff hugo.toml` 显示了本任务以外的改动，用 `git add -p` 只暂存本任务的部分。

---

### Task 4: 首页

**Files:**
- Create: `layouts/partials/home/custom.html`
- Create: `layouts/partials/topic-cards.html`
- Create: `layouts/partials/post-row.html`
- Modify: `hugo.toml`：`[params.homepage] layout = "custom"`；`[menu]` 改为三项：文章 `/posts/`（weight 1）、专题 `/categories/`（weight 2）、RSS `/index.xml`（weight 3）
- Modify: `tools/tests/test_build.py`

**Interfaces:**
- Consumes: `site.Data.topics.topic`（Task 2）；`.sk-hero`、`.sk-card`、`.sk-row`、`.sk-tag`、`.sk-serif`（Task 3）
- Produces:
  - `partial "topic-cards.html" site`：输出 `<div class="sk-topics grid …">`，内含 6 个 `<a class="sk-card sk-topic" href="{{ (site.GetPage (printf "/categories/%s" .name)).RelPermalink }}">`。每个链接里依次是专题名、说明和 `<span class="sk-count">N 篇</span>`。
  - `partial "post-row.html" .`（参数是一个 Page）：输出 `<a class="sk-row" href=…>`，内含标题、`<span class="sk-tag">专题名</span>`、`<time>2006-01-02</time>`，以及 `.Summary | plainify | truncate 80` 的摘要。

- [ ] **Step 1: 写失败的测试**

```python
class TestHome(unittest.TestCase):
    def setUp(self): self.h = page('index.html')
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
            rel = urllib.parse.unquote(c.attrs['href']).lstrip('/').removeprefix('./')
            self.assertTrue((BUILD / rel / 'index.html').exists(), rel)
    def test_ten_recent_rows(self):
        self.assertEqual(len(self.h.select('a', 'sk-row')), 10)
    def test_recent_includes_newest_by_date(self):
        newest = max((p for p in posts() if not p.meta.get('draft')), key=lambda p: str(p.meta['date']))
        self.assertIn(newest.meta['title'], self.h.select('a', 'sk-row')[0].text)
    def test_more_link(self):
        self.assertIn('查看全部 42 篇', self.h.raw)
    def test_menu(self):
        nav = self.h.raw
        for label in ('文章', '专题', 'RSS'): self.assertIn(f'>{label}<', nav.replace('\n', '').replace(' ', ''))
```

`EXPECTED` 在 `test_content.py` 中定义。把它挪到 `helpers.py` 里，两个测试文件共同导入。

`relativeURLs = true` 会让 `href` 变成相对路径（如 `categories/…`），测试已经用 `lstrip` 和 `removeprefix` 处理了这种情况。

- [ ] **Step 2: 运行，确认失败**

Run: `python -m unittest tools.tests.test_build.TestHome -v`
Expected: FAIL。

- [ ] **Step 3: 写三个模板，并修改 `hugo.toml`**

- 首页按以下顺序输出：
  - `<section class="sk-hero">`：高度 `min-h-[60vh]`，手机端用 `min-h-[auto] py-16`；内含 `h1.sk-serif`（`site.Title`）、副标题、`site.Params.description`，以及两个按钮「浏览全部文章」和「RSS 订阅」。
  - `<h2>专题</h2>`，下面是 `topic-cards`。
  - `<h2>最新文章</h2>`，下面是 10 行 `post-row`，数据来自 `(where site.RegularPages "Section" "posts").ByDate.Reverse | first 10`。
  - 最后是「查看全部 {{ len 上述集合 }} 篇 →」链接。
- 卡片网格使用 `grid grid-cols-2 lg:grid-cols-3 gap-4`。

- [ ] **Step 4: 运行测试，确认通过**

Run: `python -m unittest discover -s tools/tests -v`
Expected: 全部 PASS。

- [ ] **Step 5: 提交**

```bash
git add layouts/partials/home/custom.html layouts/partials/topic-cards.html layouts/partials/post-row.html hugo.toml tools/tests
git commit -m "feat: 深空星图首页：主视觉、专题入口与最新文章"
```

---

### Task 5: 文章页

**Files:**
- Modify: `layouts/_default/single.html`
- Create: `layouts/partials/related-topic.html`
- Modify: `tools/tests/test_build.py`

**Interfaces:**
- Consumes: `post-row.html`（Task 4）；`.sk-article`（Task 3）
- Produces: `partial "related-topic.html" .` 输出 `<aside class="sk-related">`。内容是同专题中除本文以外、按日期倒序排列的前 3 篇，每篇一个 `post-row`。同专题没有其他文章时，整个 aside 不输出。

- [ ] **Step 1: 写失败的测试**

```python
class TestArticle(unittest.TestCase):
    def test_title_meta_present(self):
        h = page('posts/qidao/index.html')
        self.assertIn('炁道：第九卦的创立与三态易学体系的开启', h.select('h1')[0].text)
        self.assertTrue(h.select('time') or '分钟' in h.raw)
    def test_duplicate_body_h1_marked(self):
        # 正文里与标题重复的 h1 被加上 sk-dup-title 类，由 CSS 隐藏
        h = page('posts/qidao/index.html')
        self.assertEqual(len(h.select('h1', 'sk-dup-title')), 1)
    def test_quote_first_article_keeps_quote(self):
        h = page('posts/superconducting-qutrit/index.html')
        self.assertTrue(h.select('blockquote'))
        self.assertEqual(len(h.select('h1', 'sk-dup-title')), 1)
    def test_toc_only_with_three_h2(self):
        for p in posts():
            if p.meta.get('draft'): continue
            n = sum(1 for l in p.body.splitlines() if l.startswith('## '))
            h = page(f"posts/{p.meta.get('slug', p.slug)}/index.html")
            self.assertEqual(bool(h.select('div', 'toc')), n >= 3, p.slug)
    def test_related_excludes_self_and_caps_at_three(self):
        h = page('posts/weilai-fu-gaowei-xiaoyaoyou/index.html')
        rows = [r for a in h.select('aside', 'sk-related') for r in a.children if 'sk-row' in r.attrs.get('class', '')]
        self.assertEqual(len(rows), 2)
        self.assertNotIn('未来赋', ' '.join(r.text for r in rows))
        self.assertEqual(len(page('posts/qidao/index.html').select('aside', 'sk-related')[0].children), 3)
    def test_share_and_pagination(self):
        h = page('posts/qidao/index.html').raw
        self.assertIn('share', h)            # share.html 的根元素类名，以实际文件为准
        self.assertIn('article-pagination', h)
```

`test_toc_only_with_three_h2` 用的 slug：文章 front matter 里有 `slug` 时以它为准，没有时用文件名。Blowfish 的目录容器带有 `toc` 类。先看一眼 `layouts/partials/share.html` 根元素的实际类名，把 `'share'` 替换成确切值。

- [ ] **Step 2: 运行，确认失败**

Run: `python -m unittest tools.tests.test_build.TestArticle -v`
Expected: FAIL。

- [ ] **Step 3: 重写 `single.html`**

以 `themes/blowfish/layouts/_default/single.html` 为底本复制一份，在副本上做以下修改：

1. 目录开关：`$enableToc` 改为 `and (site.Params.article.showTableOfContents | default true) (ge (len (findRE "<h2" .Content)) 3)`。
2. `.article-content` 外面包一层 `<div class="sk-article">`。
3. 正文输出 `.Content` 前先做一次替换：如果正文中第一个 `<h1 …>…</h1>` 的纯文本等于 `.Title`，就给它加上 `class="sk-dup-title"`。用 `replaceRE` 只替换第一处（`replaceRE` 的第 4 个参数传 `1`）。比较标题时，两边都先 `plainify`、去掉首尾空格。
4. `sharing-links.html` 之后插入 `{{ partial "share.html" . }}` 和 `{{ partial "related-topic.html" . }}`。保留主题原有的 `related.html`，但不启用。
5. 原文件里被注释掉的 `fab.html` 继续保持注释状态。

在 `custom.css` 中补一条：`.sk-dup-title { display: none }`。

- [ ] **Step 4: 写 `related-topic.html`**

用 `site.Taxonomies.categories` 取本文第一个分类下的页面，排除 `$.Permalink` 相同的那篇，取 `ByDate.Reverse | first 3`。

- [ ] **Step 5: 运行测试，确认通过**

Run: `python -m unittest discover -s tools/tests -v`
Expected: 全部 PASS。

- [ ] **Step 6: 提交**

```bash
git add layouts/_default/single.html layouts/partials/related-topic.html assets/css/custom.css tools/tests/test_build.py
git commit -m "feat: 文章页恢复标题、目录与导航，新增同专题推荐"
```

---

### Task 6: 列表页与专题总览

**Files:**
- Modify: `layouts/_default/list.html`：只把 `range $paginator.Pages` 里的 `article-link/simple.html` 换成 `post-row.html`，并在 header 下方加专题说明。`.Paginate` 那一行不动。
- Create: `layouts/_default/terms.html`
- Modify: `tools/tests/test_build.py`

**Interfaces:**
- Consumes: `post-row.html`、`topic-cards.html`、`site.Data.topics.topic`
- Produces: 专题页 header 下方输出 `<p class="sk-topic-desc">`。说明文字按页面标题去 `data/topics.toml` 里查，查不到就不输出。

- [ ] **Step 1: 写失败的测试**

```python
class TestLists(unittest.TestCase):
    def test_posts_lists_all(self):
        self.assertEqual(len(page('posts/index.html').select('a', 'sk-row')), 42)
    def test_category_page(self):
        h = page('categories/新易体系/index.html')
        self.assertEqual(len(h.select('a', 'sk-row')), 10)
        self.assertIn('九卦炁与三态易学的创立、方法与预测', h.select('p', 'sk-topic-desc')[0].text)
    def test_terms_page_cards(self):
        self.assertEqual(len(page('categories/index.html').select('a', 'sk-topic')), 6)
    def test_no_replacement_char_in_build(self):
        bad = [str(p.relative_to(BUILD)) for p in BUILD.rglob('*.html') if '�' in p.read_text(encoding='utf-8')]
        self.assertEqual(bad, [])
```

- [ ] **Step 2: 运行，确认失败**

Run: `python -m unittest tools.tests.test_build.TestLists -v`
Expected: 前 3 个测试 FAIL。

- [ ] **Step 3: 修改 `list.html`，新建 `terms.html`**

`terms.html` 结构：`define "main"`，内含 `<h1 class="sk-serif">专题</h1>`，下面是 `partial "topic-cards.html" site`。

- [ ] **Step 4: 运行全部测试，确认通过**

Run: `python -m unittest discover -s tools/tests -v`
Expected: 全部 PASS，包括 Task 1 的锁定配置测试。

- [ ] **Step 5: 提交**

```bash
git add layouts/_default/list.html layouts/_default/terms.html tools/tests/test_build.py
git commit -m "feat: 列表页与专题总览改用深空样式"
```

---

### Task 7: 浏览器人工验证

**Files:** 无新文件。只有在发现问题时，才修改 `assets/css/custom.css` 或相关模板。

- [ ] **Step 1: 启动本地预览**

在 `.claude/launch.json` 中加一项配置：名称 `hugo`，命令 `hugo server --buildFuture -d .build-server --port 1313`，端口 1313。然后用 `preview_start` 启动。

- [ ] **Step 2: 逐页检查**

按下面的组合逐一查看：

- 宽度：375px、1280px
- 外观：深色、浅色
- 页面：`/`、`/posts/`、`/categories/`、`/categories/新易体系/`、`/posts/qidao/`（有目录）、`/posts/superconducting-qutrit/`（开头是引用）、`/posts/weilai-fu-gaowei-xiaoyaoyou/`（赋体）

每个组合都对照下面的清单看一遍：

- 没有横向滚动条；
- 首页卡片在 375px 宽度下排成 2 列，1280px 下排成 3 列；
- 主视觉区的文字清楚可读；
- 浅色模式下标题和链接清楚可读（Review Focus 第 5 条）；
- 文章页没有重复的标题；
- 目录固定在右侧，滚动时不遮挡正文；
- 分享按钮和同专题推荐显示在正文末尾；
- 控制台没有报错；
- 抽查一篇文章页 `<head>` 里的 `application/ld+json` 和 `og:` 标签，与 `public/posts/qidao/index.html` 中的旧版相比，字段没有减少。

- [ ] **Step 3: 修复与复验**

每发现一个问题：修改 → `python -m unittest discover -s tools/tests` → 刷新页面复验 → 提交，提交信息格式为 `fix: <问题>`。

- [ ] **Step 4: 收尾**

- 运行 `git status`，确认本次的所有文件都已提交，并且没有把无关文件带进提交。
- 运行 `git log --oneline master..`，列出本分支的全部提交，连同截图一起交给作者审阅。
- **不推送。** 合并到 `master` 和上线，都由作者另行决定。
