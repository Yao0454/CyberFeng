#!/usr/bin/env python3
"""
自动更新 README 的脚本
用于获取仓库的实时统计信息并更新 README.md
"""

import os
import re
from datetime import datetime, timezone, timedelta
from github import Github

def get_github_client():
    """初始化 GitHub 客户端"""
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable is not set")
    return Github(token)

def get_repo(g=None):
    """获取仓库对象"""
    if g is None:
        g = get_github_client()
    
    # 从环境变量获取仓库名称，否则使用默认值
    repo_name = os.environ.get('GITHUB_REPOSITORY', 'Yao0454/CyberFeng')
    return g.get_repo(repo_name)

def get_repo_stats(repo):
    """获取仓库统计信息"""
    utc_now = datetime.now(timezone.utc)
    # 北京时间 = UTC + 8
    beijing_now = utc_now + timedelta(hours=8)
    
    stats = {
        'stars': repo.stargazers_count,
        'forks': repo.forks_count,
        'watchers': repo.subscribers_count,
        'issues': repo.open_issues_count,
        'contributors': repo.get_contributors().totalCount,
        'updated_time': utc_now.strftime('%Y-%m-%d %H:%M:%S UTC'),
        'updated_time_cn': beijing_now.strftime('%Y年%m月%d日 %H:%M 北京时间'),
    }
    
    return stats

def get_recent_commits(repo, limit=5):
    """获取最近的提交记录"""
    
    commits = []
    for commit in repo.get_commits()[:limit]:
        commits.append({
            'sha': commit.sha[:7],
            'message': commit.commit.message.split('\n')[0],
            'author': commit.commit.author.name,
            'date': commit.commit.author.date.strftime('%Y-%m-%d'),
            'url': commit.html_url
        })
    
    return commits

def generate_stats_section(stats):
    """生成统计信息区域"""
    return f"""## 📊 项目数据（实时更新）

<div align="center">

![Stars](https://img.shields.io/github/stars/Yao0454/CyberFeng?style=for-the-badge&logo=github)
![Forks](https://img.shields.io/github/forks/Yao0454/CyberFeng?style=for-the-badge&logo=github)
![Issues](https://img.shields.io/github/issues/Yao0454/CyberFeng?style=for-the-badge&logo=github)
![Contributors](https://img.shields.io/github/contributors/Yao0454/CyberFeng?style=for-the-badge&logo=github)
![Last Commit](https://img.shields.io/github/last-commit/Yao0454/CyberFeng?style=for-the-badge&logo=github)

</div>

| 指标 | 数值 |
|------|------|
| ⭐ Stars | {stats['stars']} |
| 🔱 Forks | {stats['forks']} |
| 👀 Watchers | {stats['watchers']} |
| 📝 Open Issues | {stats['issues']} |
| 👥 Contributors | {stats['contributors']} |
| 📅 最后更新 | {stats['updated_time_cn']} |

"""

def generate_recent_commits_section(commits):
    """生成最近提交区域"""
    commits_text = ""
    for commit in commits:
        commits_text += f"- [`{commit['sha']}`]({commit['url']}) {commit['message']} - *{commit['author']}* ({commit['date']})\n"
    
    return f"""## 📝 最近提交

{commits_text}
"""

def update_readme():
    """更新 README.md"""
    readme_path = 'README.md'
    
    # 读取当前 README
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 获取 GitHub 客户端和仓库对象
    g = get_github_client()
    repo = get_repo(g)
    
    # 获取数据
    stats = get_repo_stats(repo)
    commits = get_recent_commits(repo, 5)
    
    # 生成新的区域
    stats_section = generate_stats_section(stats)
    commits_section = generate_recent_commits_section(commits)
    
    # 定义标记
    stats_start = "<!-- STATS_START -->"
    stats_end = "<!-- STATS_END -->"
    commits_start = "<!-- COMMITS_START -->"
    commits_end = "<!-- COMMITS_END -->"
    
    # 如果存在标记，替换内容
    if stats_start in content and stats_end in content:
        pattern = f"{re.escape(stats_start)}.*?{re.escape(stats_end)}"
        replacement = f"{stats_start}\n{stats_section}\n{stats_end}"
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    else:
        # 如果不存在标记，在标题后插入
        # 在第一个 ## 之前插入
        first_section = content.find('\n## ')
        if first_section != -1:
            insert_text = f"\n{stats_start}\n{stats_section}\n{stats_end}\n"
            content = content[:first_section] + insert_text + content[first_section:]
    
    # 更新最近提交区域
    if commits_start in content and commits_end in content:
        pattern = f"{re.escape(commits_start)}.*?{re.escape(commits_end)}"
        replacement = f"{commits_start}\n{commits_section}\n{commits_end}"
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    else:
        # 如果不存在，添加到末尾（在 "开源说明" 之前）
        license_section = content.find('## 📄 开源说明')
        if license_section != -1:
            insert_text = f"\n{commits_start}\n{commits_section}\n{commits_end}\n"
            content = content[:license_section] + insert_text + content[license_section:]
        else:
            # 如果找不到开源说明，添加到末尾
            content += f"\n{commits_start}\n{commits_section}\n{commits_end}\n"
    
    # 写入 README
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ README 已更新！")
    print(f"📊 Stars: {stats['stars']}, Forks: {stats['forks']}, Issues: {stats['issues']}")
    print(f"📅 更新时间: {stats['updated_time']}")

if __name__ == '__main__':
    update_readme()
