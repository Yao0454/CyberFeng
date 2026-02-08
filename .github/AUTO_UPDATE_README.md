# README 自动更新说明

本文档说明 CyberFeng 项目的 README 自动更新功能。

## 功能概述

README.md 文件会自动更新以下内容：

### 1. 项目统计数据
- Stars（收藏数）
- Forks（分支数）
- Watchers（关注数）
- Open Issues（开放问题数）
- Contributors（贡献者数）
- 最后更新时间

### 2. 最近提交
- 最近 5 条提交记录
- 提交信息、作者和日期
- 每条提交都有链接指向 GitHub

## 更新时机

README 会在以下情况自动更新：

1. **定时更新**：每天北京时间早上 8 点（UTC 00:00）
2. **推送触发**：每次推送到 `main` 分支
3. **手动触发**：在 GitHub Actions 页面点击 "Run workflow"

## 技术架构

### 文件结构

```
.github/
├── workflows/
│   └── update-readme.yml      # GitHub Actions 工作流配置
└── scripts/
    └── update_readme.py       # Python 更新脚本
```

### 工作流程

1. GitHub Actions 按照设定的时间触发
2. 检出仓库代码
3. 安装 Python 依赖（PyGithub）
4. 运行 `update_readme.py` 脚本
5. 脚本通过 GitHub API 获取最新数据
6. 更新 README.md 中的标记区域
7. 自动提交并推送更改

### 标记区域

README.md 中使用特殊注释标记来指定更新区域：

```markdown
<!-- STATS_START -->
这里会自动插入项目统计数据
<!-- STATS_END -->

<!-- COMMITS_START -->
这里会自动插入最近提交记录
<!-- COMMITS_END -->
```

## 自定义配置

### 修改更新频率

编辑 `.github/workflows/update-readme.yml` 文件中的 cron 表达式：

```yaml
on:
  schedule:
    - cron: '0 0 * * *'  # 每天 UTC 00:00 (北京时间 08:00)
```

### 修改显示内容

编辑 `.github/scripts/update_readme.py` 文件：

- 修改 `get_recent_commits(limit=5)` 中的 `limit` 参数可以改变显示的提交数量
- 修改 `generate_stats_section()` 和 `generate_recent_commits_section()` 函数可以自定义显示格式

### 添加新的统计项

在 `get_repo_stats()` 函数中添加新的统计项，例如：

```python
stats = {
    'stars': repo.stargazers_count,
    'total_commits': repo.get_commits().totalCount,  # 新增
    # ... 其他统计
}
```

然后在 `generate_stats_section()` 中显示这个新项。

## 权限说明

工作流使用 GitHub Actions 自带的 `GITHUB_TOKEN`，具有以下权限：

- `contents: write` - 允许修改和推送 README.md
- 读取仓库统计信息的权限（通过 GitHub API）

无需额外配置 Personal Access Token。

## 故障排查

### 工作流未运行

1. 检查 GitHub Actions 是否启用
2. 查看 Actions 页面的运行日志
3. 确认 `main` 分支存在

### 更新失败

1. 查看 Actions 运行日志中的错误信息
2. 确认 README.md 中存在正确的标记注释
3. 确认 Python 依赖安装成功

### 提交冲突

如果在 README 手动编辑和自动更新之间产生冲突：

1. 手动解决 README.md 的合并冲突
2. 确保保留 `<!-- STATS_START -->` 等标记
3. 推送解决后的版本

## 最佳实践

1. **不要手动编辑标记区域内的内容**，它们会被自动覆盖
2. **保留所有 `<!-- ... -->` 标记**，删除它们会导致更新失败
3. **在标记区域外添加内容**，这样不会影响自动更新
4. 如需大幅修改 README 结构，先暂时禁用工作流

## 扩展建议

可以考虑添加的功能：

- 显示项目语言分布
- 显示代码行数统计
- 显示开发活跃度图表
- 集成更多的 GitHub Badges
- 添加贡献者列表
- 显示最受欢迎的 Issues

---

*如有问题，请在 Issues 中反馈。*
