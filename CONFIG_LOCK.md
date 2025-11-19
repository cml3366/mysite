# Configuration Lock Guide

## ⚠️ CRITICAL: Do NOT Modify These Configurations

**This configuration is locked and tested. Modifying it may cause articles to disappear!**

## 🔒 Locked Configurations

### 1. `hugo.toml`

**DO NOT CHANGE:**
```toml
buildFuture = true        # MUST be true
pagerSize = 50            # MUST be 50 or larger
showRecentItems = 20      # MUST be 20 or larger
```

### 2. `.github/workflows/deploy.yml`

**DO NOT CHANGE:**
```yaml
run: hugo --minify --buildFuture  # --buildFuture MUST be included
```

### 3. `layouts/_default/list.html`

**DO NOT CHANGE:**
```go
{{ $paginator := .Paginate (.Pages.ByDate.Reverse) 50 }}  # 50 MUST be kept
```

## ✅ Safe to Modify

- `title`, `tagline`, `description` - SEO settings
- `keywords` - SEO keywords
- `[params.Author]` - Author info
- `[menu]` - Menu configuration

## 📋 Pre-Push Checklist

Before pushing, verify:
- [ ] `buildFuture = true` in `hugo.toml`
- [ ] `--buildFuture` in `.github/workflows/deploy.yml`
- [ ] `pagerSize = 50` in `hugo.toml`
- [ ] All 19 articles still visible

## 🔄 Restore Configuration

If something breaks, restore from `配置备份/` directory.

---

**Last Updated**: 2024
**Status**: ✅ All 19 articles working

