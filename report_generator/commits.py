import os
from datetime import datetime
from pathlib import Path

import pytz
from dotenv import load_dotenv
from github import Github, Repository, GithubException

load_dotenv()
TASK_ID_REGEX = r"\WPiRogueToolSuite\/project-management#([0-9]+)\W*?$"
ISSUE_DESCRIPTION_REGEX = r"Description[:\s]+(.*?)Tasks"
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')


def first_day_of_current_month():
    now = datetime.now(pytz.utc)
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def list_repositories():
    g = Github(GITHUB_TOKEN)
    org = g.get_organization('PiRogueToolSuite')
    return org.get_repos(type='public', sort='pushed')


def list_commits(repository: Repository):
    commits = []
    try:
        commits = repository.get_commits(since=first_day_of_current_month())
    except:
        pass
    return commits


def format_commit_message(commit):
    commit_lines = commit.commit.message.split('\n')
    text = f'* [{commit.author.name}] {commit_lines[0]}'
    for l in commit_lines[1:]:
        text += f'\n  {l}'
    text += '\n'
    return text


def dump_commit_list(output_file: Path):
    with output_file.open('w') as f:
        f.write('# List of commits\n')
        for repo in list_repositories():
            commits = list_commits(repo)
            if commits:
                f.write(f'\n## {repo.name}\n')
                for commit in commits:
                    f.write(format_commit_message(commit))
                f.write('')


if __name__ == '__main__':
    output_dir = Path('./output')
    os.makedirs(output_dir, exist_ok=True)
    dump_commit_list(output_dir / 'commits.md')
    print(f'Report generated at {output_dir}')