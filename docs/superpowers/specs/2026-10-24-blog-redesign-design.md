# blog.cml3366.cn 改版设计：深空星图

- 日期：2026-10-24
- 分支：`redesign/shenkong`
- 状态：待审阅

## 1. 目标

把整站统一成「宇宙之光 × 古典之韵」的气质，并让首页成为门面：访客一进来就知道这是写易学、新易与量子的站，能按专题找到文章。

成功标准：

1. 首页、列表页、专题页、文章页使用同一套深空配色，不再出现深色外壳套白卡片的拼接感。
2. 首页有主视觉、六个专题入口、最新 10 篇文章。
3. 42 篇正式文章全部归入专题，正文没有乱码。
4. 文章页有标题、日期、阅读时长、目录、上一篇和下一篇导航，以及同专题推荐。
5. 三处锁定配置不变，`hugo --minify --buildFuture` 构建出的文章数和改版前一致。

## 2. 约束

- **锁定配置不动**：`hugo.toml` 中的 `buildFuture = true`、`[pagination] pagerSize = 50`，`.github/workflows/deploy.yml` 中的 `--buildFuture`，`layouts/_default/list.html` 中分页的 `50`。
- **不改主题源码**：`themes/blowfish` 是 git submodule（v2.91.0）。所有改动都通过项目根目录下的覆盖文件实现。
- **不加载网络字体**：大陆访问 Google Fonts 很慢，只使用系统字体栈。
- **不改动文章原意**：正文只做乱码恢复；front matter 只新增 `categories`，以及把两篇占位稿改为草稿。
- 现有的 SEO 结构化数据、`extend-head.html`、`share.html`、Google 验证文件保持原样。

## 3. 第 0 步：恢复正文乱码

### 3.1 现状

2025-11-18 的提交 `9d9dac8` 把 17 篇文章正文中的部分汉字写坏了：行尾汉字变成 `�?`，正文中出现大量 `U+FFFD`。之后几次「修复编码」只修好了 front matter，正文一直没有恢复，线上显示的就是损坏后的版本。

| 文件 | 最后完好版本 |
|---|---|
| `badao-jiugua-san-tai-yongxian.md` | `e3ca6a3` |
| `binary-ternary-quantum.md` | `922a23f` |
| `dongfang-zhexue-xiandai-wuli.md` | `8f6c0a9` |
| `erqian-liuyao.md` | `cd921bd` |
| `hetu-luoshu-quantum-entanglement.md` | `340d2db` |
| `huangdi-neijing-taisu-research-postscript.md` | `23d1e69` |
| `physics-quantum-jiugua-qi.md` | `a8a1b05` |
| `qi-neiwaijing-sanyuan.md` | `3e31b54` |
| `qidao.md` | `23d1e69` |
| `qigua-tianyan.md` | `23d1e69` |
| `quantum-computing-jiugua-qi.md` | `950797e` |
| `quantum-entanglement-mingli.md` | `f6e504d` |
| `quantum-jiugua-qi.md` | `a3bd58e` |
| `quantum-yixue-system-framework.md` | `7e1f654` |
| `xin-yi-quantum.md` | `5c1f0ff` |
| `xinyi-preface.md` | `a9da339` |
| `zhengzong-yuce.md` | `740e893` |

`liuyao-jiugua-81-model.md` 和 `weilai-fu-gaowei-xiaoyaoyou.md` 被初筛标出，复查后确认没有损坏：它们的行尾本来就是半角问号。

### 3.2 恢复方法

1. 每篇文章的**正文**取上表中的完好版本，**front matter** 保留当前工作区的版本（里面有日期、SEO 标题、标签和描述）。
2. 恢复前，先比较「完好版本」与「当前版本」的正文：把当前版本中被写坏的字符当作通配符，其余文字必须逐字一致。逐字一致才说明完好版本之后正文没有被改过别的内容。出现不一致的文章暂不恢复，单独列出，由作者决定。
3. 恢复后检查：所有文章都不含 `U+FFFD`，并且都能按 UTF-8（无 BOM）解码。
4. 这一步单独提交，和样式改动分开，方便回看。

## 4. 配色与字体

### 4.1 配色方案 `shenkong`

新建 `assets/css/schemes/shenkong.css`，按 Blowfish 配色文件的格式定义 `--color-neutral-*`、`--color-primary-*`、`--color-secondary-*` 三组色阶（每组 50–950 共 11 级，值为 RGB 三元组）。`hugo.toml` 中设置 `colorScheme = 'shenkong'`（原来的 `'dark'` 不是有效的配色名），默认外观保持 `dark`。

| 用途 | 颜色 | 对应色阶 |
|---|---|---|
| 页面底色 | `#0a0f1f` | neutral-900 |
| 卡片底色 | 白色 5% 透明 | 在 `custom.css` 中定义 |
| 卡片边框 | 淡金 25% 透明 | 在 `custom.css` 中定义 |
| 正文 | `#e8e6df` | neutral-100 |
| 次要文字 | `#a3a7b8` | neutral-400 |
| 主色（标题、链接、标签） | `#f3d58b` | primary-300 |
| 主色悬停 | `#c9a34e` | primary-500 |
| 辅色（引用线、行内代码、分割线） | `#7d97d6` | secondary-400 |

浅色模式保留切换按钮，使用同一套色阶反转：米白底 neutral-50，深金字 primary-700。

### 4.2 字体

| 用途 | 字体栈 |
|---|---|
| 站名、标题 | `"Songti SC", "Noto Serif CJK SC", "Source Han Serif SC", SimSun, serif`，字间距 0.08–0.14em |
| 正文 | `"PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif` |

文章正文字号 17px，行高 1.85，最大宽度约 38 个汉字（`max-width: 40rem`）。

### 4.3 背景

- 首页主视觉区：`#1b2a52` 到 `#0a0f1f` 的径向渐变，叠加用 `radial-gradient` 绘制的 CSS 星点，再叠一层很淡的九宫纹路。不额外加载图片。
- 其他页面：纯底色，页顶带一条很淡的渐变。

### 4.4 退场

- 删除 `static/css/reader.css`，同时删除 `hugo.toml` 中的 `customCSS = ["/css/reader.css"]`。
- 新的覆盖样式放在 `assets/css/custom.css`，由 Blowfish 自动加载并压缩打包。

## 5. 首页

`hugo.toml` 中设置 `homepage.layout = "custom"`，新建 `layouts/partials/home/custom.html`。页面由三块组成：

### 5.1 主视觉

- 站名「宇宙之光 × 古典之韵」：宋体、淡金色。
- 副标题：从古典智慧到量子科学。
- 简介：读取 `site.Params.description`。
- 两个按钮：「浏览全部文章」指向 `/posts/`，「RSS 订阅」指向 `/index.xml`。
- 高度：桌面端约 60vh，手机端自适应内容。

### 5.2 专题入口

六张卡片，桌面端 3 列，手机端 2 列。每张卡片包含专题名、说明和篇数。篇数由 `site.Taxonomies.categories` 在构建时统计。点击卡片进入 `/categories/<专题名>/`。

| 专题 | 卡片说明 |
|---|---|
| 新易体系 | 九卦炁与三态易学的创立、方法与预测 |
| 量子与易学 | 以量子理论重读卦象、命理与意识 |
| 三进制与九卦 | 从二进制八卦到三进制九卦的升维 |
| 古典研究 | 河图洛书、黄帝内经与炁卦天演 |
| 科学前沿 | 量子物理与量子计算的新进展 |
| 哲思与赋 | 东西哲学之思与赋体之作 |

专题顺序和说明文字写在 `data/topics.toml` 里，首页和专题页都从这个文件读取，以后改说明只需改一处。（项目根目录已有一个与博客无关的 `data/valuation-tasks.json`，它不会被模板读取，不受影响。）

### 5.3 最新文章

- 取 `mainSections` 中的文章，按日期倒序取前 10 篇。
- 每篇一行，包括标题、专题标签、日期和摘要，悬停时整行微微发亮。
- 列表末尾放「查看全部 N 篇 →」链接，指向 `/posts/`，N 由模板统计。

### 5.4 导航

`hugo.toml` 中的 `[menu]` 改为：文章 `/posts/`、专题 `/categories/`、RSS `/index.xml`。

原来的 `layouts/partials/recent-articles/list.html` 不再使用，但文件保留，方便回退。

## 6. 专题分类

每篇文章的 front matter 新增一行 `categories = ['<专题名>']`，原有 `tags` 不动。专题页使用中文路径，例如 `/categories/新易体系/`。

- **新易体系（10）**：`qidao` · `xinyi-preface` · `xin-yi-quantum` · `quantum-theory-xinyi-philosophy` · `xinyi-quantum-liuyao-fusion` · `xinyi-quantum-prediction-design` · `probability-and-xinyi` · `zhengzong-yuce` · `erqian-liuyao` · `uploaded-article`（前知）
- **量子与易学（11）**：`quantum-jiugua-qi` · `physics-quantum-jiugua-qi` · `quantum-computing-jiugua-qi` · `quantum-yixue-system-framework` · `quantum-entanglement-mingli` · `quantum-life-mingli` · `bashi-yi-gua-qigua-yunsuan-quantum-entanglement` · `qigua-san-tai-quantum-entanglement` · `coin-divination-quantum-observation` · `consciousness-quantum-xinyi` · `personality-81-quantum`
- **三进制与九卦（8）**：`binary-and-bagua` · `ternary-and-jiugua` · `binary-ternary-quantum` · `ternary-and-quantum-mechanics` · `badao-jiugua-san-tai-yongxian` · `bagua-jiugua-multidimensional-proof` · `liuyao-jiugua-81-model` · `yinyang-wuxing-ternary-quantum`
- **古典研究（5）**：`hetu-luoshu-qigua-zhonggong` · `hetu-luoshu-quantum-entanglement` · `huangdi-neijing-taisu-research-postscript` · `qi-neiwaijing-sanyuan` · `qigua-tianyan`
- **科学前沿（5）**：`nobel-2025-macroscopic-tunneling` · `photon-wave-particle-key` · `quantum-error-correction` · `superconducting-qutrit` · `decoherence-bell-entanglement`
- **哲思与赋（3）**：`dongfang-zhexue-xiandai-wuli` · `weilai-fu-gaowei-xiaoyaoyou` · `weitegensitan-zhexue-yanjiu-liubian-buju`

`first.md` 和 `hello-world.md` 改为 `draft = true`。

## 7. 文章页

现在的 `layouts/_default/single.html` 只输出正文和分享按钮，把 Blowfish 的标题、元信息、目录和导航全部挡掉了。改版后的模板：

1. **页头**：标题（宋体、淡金色）、日期、阅读时长、专题标签。
2. **正文**：Blowfish 的 `prose` 排版，使用第 4 节的字体和行宽。
   - 正文第一行如果是与标题重复的 `# 标题`，用 CSS 隐藏（`.article-content > h1:first-child`），不改源文件。部分文章正文开头是一段引用，后面才是 `# 标题`，这种情况也要隐藏，具体选择器在实现时验证。
   - `h2` 前加淡金色「◆」，`h3` 不加装饰。
   - 引用块：星蓝色左边线加浅底色。代码块：卡片底色加圆角。
   - 表格：细边框，表头使用淡金色文字。
   - 图片：居中，带圆角。
3. **目录**：有 3 个及以上 `h2` 时显示。桌面端（≥1024px）显示在右侧并固定在屏幕上，手机端折叠在正文上方。使用 Blowfish 自带的目录组件。
4. **分享**：`partial "share.html"` 放在正文末尾，样式改成深空配色。
5. **同专题文章**：列出同专题中除本文以外的 3 篇，按日期倒序。
6. **上一篇和下一篇**：使用 Blowfish 自带的文章导航组件。
7. `fab.html` 和 `status-panel.html` 继续保持注释状态。

`layouts/partials/article-structured-data.html` 中的结构化数据保持不变。

## 8. 列表页

- `/posts/` 和 `/categories/<专题>/` 沿用首页「最新文章」的行式样。
- 专题页顶部显示专题名，以及 `data/topics.toml` 中的说明。
- `/categories/` 总览页显示六张专题卡片，与首页的卡片一致。
- `layouts/_default/list.html` 中的 `.Paginate (.Pages.ByDate.Reverse) 50` 不改。

## 9. 改动文件一览

| 操作 | 文件 |
|---|---|
| 新增 | `assets/css/schemes/shenkong.css` |
| 新增 | `assets/css/custom.css` |
| 新增 | `layouts/partials/home/custom.html` |
| 新增 | `data/topics.toml` |
| 新增 | `layouts/_default/terms.html`（专题总览） |
| 新增 | `layouts/partials/related-topic.html`（同专题文章） |
| 修改 | `hugo.toml`：`colorScheme`、`customCSS`、`homepage.layout`、`menu` |
| 修改 | `layouts/_default/single.html` |
| 修改 | `layouts/_default/list.html`（只改展示部分，不改分页） |
| 修改 | `content/posts/*.md`：17 篇恢复正文，42 篇新增 `categories`，2 篇改为草稿 |
| 删除 | `static/css/reader.css` |

## 10. 验证

1. `hugo --minify --buildFuture` 构建无报错、无警告。
2. 构建结果中 `/posts/` 列出 42 篇文章，六个专题的篇数之和为 42。
3. 用脚本扫描 `content/posts/*.md` 和 `public/**/*.html`，确认不含 `U+FFFD`。
4. 用 `hugo server` 在浏览器中检查首页、`/posts/`、一个专题页、三篇文章页（一篇有目录、一篇开头是引用、一篇赋体），宽度分别为 375px 和 1280px，深色和浅色模式各看一遍。
5. 检查锁定配置：确认 `buildFuture = true`、`pagerSize = 50`、`--buildFuture`、`list.html` 中的 `50` 都还在。
6. 抽查文章页 `<head>` 中的结构化数据和 Open Graph 标签，与改版前一致。

## 11. 不在本次范围

- 工作区里与博客无关的数据资产原型（`asset_*.py`、`tests/`、`extension/`、`data/valuation-tasks.json`）不处理，也不提交。
- `public/` 中已提交的旧构建产物不在本次处理范围。部署由 GitHub Actions 重新构建。
- 推送到 `master` 并上线前，需要作者单独确认。
