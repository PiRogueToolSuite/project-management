import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytz
from dotenv import load_dotenv
from github import Github, Repository

load_dotenv()
TASK_ID_REGEX = r"\WPiRogueToolSuite\/project-management#([0-9]+)\W*?$"
ISSUE_DESCRIPTION_REGEX = r"Description[:\s]+(.*?)Tasks"
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')


def first_day_of_current_month():
    now = datetime.now(pytz.utc)
    now -= timedelta(days=28)
    return now
    # return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0, year=2024, month=12)
    # return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def list_repositories():
    g = Github(GITHUB_TOKEN)
    org = g.get_organization('PiRogueToolSuite')
    return org.get_repos(type='public', sort='pushed')


def list_commits(repository: Repository, since: str):
    commits = []
    try:
        s = datetime.strptime(since, '%d-%m-%Y')
        commits = repository.get_commits(since=s)
    except:
        pass
    return commits


def format_commit_message(commit):
    commit_lines = commit.commit.message.split('\n')
    name = 'Unknown'
    if commit.author: name = commit.author.name
    text = f'* *{str(commit.commit.author.date)[:10]}* @{name} [`#{commit.sha[-7:]}`]({commit.html_url})\t{commit_lines[0]}'
    # for l in commit_lines[1:]:
    #     text += f'\n  {l}'
    # text += '\n'
    return text


def dump_commit_list(output_file: Path, since: str):
    with output_file.open('w') as f:
        f.write('# List of commits\n')
        for repo in list_repositories():
            commits = list_commits(repo, since)
            if commits:
                f.write(f'\n## {repo.name}\n')
                for commit in commits:
                    f.write(f'{format_commit_message(commit)}\n')
                f.write('')


if __name__ == '__main__':
    output_dir = Path('./output')
    s = sys.argv[1]
    os.makedirs(output_dir, exist_ok=True)
    dump_commit_list(output_dir / 'commits.md', s)
    print(f'Report generated at {output_dir}')
