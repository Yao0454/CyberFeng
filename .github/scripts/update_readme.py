#!/usr/bin/env python3
"""
更新 README.md 的脚本，自动添加以下信息：
- GitHub 统计数据（stars, forks, issues）
- 最近的提交记录
- 项目活跃度指标
- 最后更新时间
"""

import os
import re
from datetime import datetime
from github import Github
import pytz

# 从环境变量获取 GitHub token
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
REPO_NAME = 'Yao0454/CyberFeng'

def get_repo_stats():
    """获取仓库统计信息"""
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    
    stats = {
        'stars': repo.stargazers_count,
        'forks': repo.forks_count,
        'watchers': repo.subscribers_count,
        'open_issues': repo.open_issues_count,
        'size': repo.size,  # KB
    }
    
    return stats, repo

def get_recent_commits(repo, count=5):
    """获取最近的提交记录"""
    commits = repo.get_commits()
    recent = []
    
    for i, commit in enumerate(commits):
        if i >= count:
            break
        
        # 转换为北京时间
        beijing_tz = pytz.timezone('Asia/Shanghai')
        commit_time = commit.commit.author.date.replace(tzinfo=pytz.UTC).astimezone(beijing_tz)
        
        recent.append({
            'sha': commit.sha[:7],
            'message': commit.commit.message.split('\n')[0],
            'author': commit.commit.author.name,
            'date': commit_time.strftime('%Y-%m-%d %H:%M'),
            'url': commit.html_url
        })
    
    return recent

def generate_stats_section(stats, recent_commits):
    """生成统计信息部分"""
    beijing_tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(beijing_tz)
    
    section = f"""
## 📊 项目统计

<div align="center">

![GitHub stars](https://img.shields.io/github/stars/{REPO_NAME}?style=social)
![GitHub forks](https://img.shields.io/github/forks/{REPO_NAME}?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/{REPO_NAME}?style=social)
![GitHub repo size](https://img.shields.io/github/repo-size/{REPO_NAME})
![GitHub language count](https://img.shields.io/github/languages/count/{REPO_NAME})
![GitHub top language](https://img.shields.io/github/languages/top/{REPO_NAME})
![GitHub last commit](https://img.shields.io/github/last-commit/{REPO_NAME})
![GitHub issues](https://img.shields.io/github/issues/{REPO_NAME})
![GitHub closed issues](https://img.shields.io/github/issues-closed/{REPO_NAME})
![GitHub pull requests](https://img.shields.io/github/issues-pr/{REPO_NAME})
![GitHub closed pull requests](https://img.shields.io/github/issues-pr-closed/{REPO_NAME})
![GitHub contributors](https://img.shields.io/github/contributors/{REPO_NAME})

</div>

### 📈 仓库数据

- ⭐ **Stars**: {stats['stars']}
- 🍴 **Forks**: {stats['forks']}
- 👀 **Watchers**: {stats['watchers']}
- 🐛 **Open Issues**: {stats['open_issues']}
- 💾 **仓库大小**: {stats['size']} KB

### 📝 最近提交

"""
    
    for commit in recent_commits:
        section += f"- [`{commit['sha']}`]({commit['url']}) {commit['message']} - *{commit['author']}* ({commit['date']})\n"
    
    section += f"\n*最后更新时间: {now.strftime('%Y年%m月%d日 %H:%M:%S')} (北京时间)*\n"
    
    return section

def update_readme():
    """更新 README.md 文件"""
    readme_path = 'README.md'
    
    # 读取当前 README
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 获取统计数据
    stats, repo = get_repo_stats()
    recent_commits = get_recent_commits(repo)
    
    # 生成新的统计部分
    stats_section = generate_stats_section(stats, recent_commits)
    
    # 定义统计部分的标记
    start_marker = '<!-- STATS:START -->'
    end_marker = '<!-- STATS:END -->'
    
    # 如果已经有统计部分，则替换它
    if start_marker in content and end_marker in content:
        pattern = f'{start_marker}.*?{end_marker}'
        replacement = f'{start_marker}\n{stats_section}\n{end_marker}'
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    else:
        # 如果没有统计部分，在 "## 📖 项目介绍" 之前插入
        insert_marker = '## 📖 项目介绍'
        if insert_marker in content:
            stats_block = f'\n{start_marker}\n{stats_section}\n{end_marker}\n\n'
            new_content = content.replace(insert_marker, stats_block + insert_marker)
        else:
            # 如果找不到插入点，添加到文件开头（标题之后）
            lines = content.split('\n')
            # 找到第一个非标题行
            insert_pos = 2  # 默认在第二行之后
            for i, line in enumerate(lines):
                if i > 0 and not line.startswith('#') and line.strip():
                    insert_pos = i
                    break
            
            stats_block = f'\n{start_marker}\n{stats_section}\n{end_marker}\n'
            lines.insert(insert_pos, stats_block)
            new_content = '\n'.join(lines)
    
    # 写回文件
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ README.md 已更新！")
    print(f"  - Stars: {stats['stars']}")
    print(f"  - Forks: {stats['forks']}")
    print(f"  - 最近提交数: {len(recent_commits)}")

if __name__ == '__main__':
    update_readme()
