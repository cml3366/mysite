---
title: "管理中心"
description: "常用链接与操作"
menu: "main"
weight: 7
---

## 快捷管理

- 打开 Obsidian（本地）：请运行 `D:\博客\open_obsidian.ps1`
- 启动本地预览：运行 `D:\博客\run_blog.ps1`
- 备份：
  - 快照：`D:\博客\snapshot_blog.ps1`
  - 镜像：`D:\博客\backup_blog.ps1`

### 新建文章（命令）

在 PowerShell 执行：

```powershell
cd C:\Users\58364\mysite
hugo new posts/你的标题.md
```

然后编辑 `content/posts/你的标题.md`，把 `draft` 改为 `false`，即可发布。

## 链接

- 站点首页：/
- RSS：/index.xml
- GitHub 仓库：https://github.com/cml3366/mysite
