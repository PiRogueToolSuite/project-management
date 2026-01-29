import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

import pytz
import jinja2
from dotenv import load_dotenv
from github import Github, Auth, Issue, Repository
from github.IssueComment import IssueComment

load_dotenv()
TASK_ID_REGEX = r"\WPiRogueToolSuite\/project-management#([0-9]+)\W*?$"
ISSUE_DESCRIPTION_REGEX = r"Description[:\s]+(.*?)Tasks"
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')


def first_day_of_current_month(reporting_date):
    # now = datetime.now()
    # return now - timedelta(days=28)
    # return now.replace(day=2, hour=0, minute=0, second=0, microsecond=0, year=2024, month=12)
    return reporting_date.replace(day=4, hour=0, minute=0, second=0, microsecond=0)


class ProjectActivity:
    def __init__(self, repository: Repository, issue: Issue, reporting_date: datetime):
        self.repository: Repository = repository
        self.issue: Issue = issue
        self.reporting_date = reporting_date
        self.tasks: list[ProjectActivity] = []
        self.reports: list[IssueComment] = []
        self.description: str = ''
        self._get_description()
        self._get_reports()
        if self.is_user_story:
            self._get_tasks()

    @property
    def has_reports(self):
        _has_reports = bool(self.reports)
        for t in self.tasks:
            _has_reports = _has_reports or t.has_reports
        return _has_reports

    @property
    def has_tasks(self):
        return bool(self.tasks)

    @property
    def is_user_story(self):
        return 'user story' in [l.name for l in self.issue.labels]

    def _get_description(self):
        issue_body = self.issue.body or ''
        # Remove bold markdown
        issue_body = issue_body.replace('**', '').strip()
        if 'Description' not in issue_body: return issue_body
        if 'Tasks' not in issue_body: issue_body += 'Tasks'
        matches = re.search(ISSUE_DESCRIPTION_REGEX, issue_body, re.MULTILINE | re.DOTALL)
        if matches:
            self.description = matches.group(1).strip()

    def _get_tasks(self):
        issue_body = self.issue.body or ''
        matches = re.finditer(TASK_ID_REGEX, issue_body, re.MULTILINE | re.IGNORECASE)
        if matches:
            for matchNum, match in enumerate(matches, start=1):
                sub_task_number = int(match.group(1))
                sub_task = self.repository.get_issue(number=sub_task_number)
                self.tasks.append(ProjectActivity(None, sub_task, self.reporting_date))

    def _get_reports(self):
        comments = self.issue.get_comments(since=first_day_of_current_month(self.reporting_date))
        for comment in comments:
            if '#### This month' in comment.body:
                self.reports.append(comment)

    def __getattr__(self, item):
        return getattr(self.issue, item)

    def __str__(self):
        self._get_description()
        s = f'[{self.issue.state}] {self.issue.title}\n'
        s += f'D: {self.description}\n'
        return s


class ProjectReport:
    def __init__(self):
        self.jinja_env = jinja2.Environment(loader=jinja2.PackageLoader('report_generator', './templates/'))
        auth = Auth.Token(GITHUB_TOKEN)
        self.github = Github(auth=auth)
        self.reporting_date = datetime.now(pytz.utc)
        self.set_reporting_date()
        self.user_stories: list[ProjectActivity] = []
        self.repository = self.github.get_repo("PiRogueToolSuite/project-management")

    def set_reporting_date(self):
        today = datetime.now(pytz.utc)
        # self.reporting_date = today - timedelta(days=28)
        self.reporting_date.replace(hour=0, minute=0, second=0, microsecond=0)
        if today.day < 10:
            # Switch to the previous month
            today = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            self.reporting_date = today - timedelta(days=1)

    def get_user_stories(self):
        _user_stories = [us for us in self.repository.get_issues(labels=['user story'], state='all')]
        _user_stories = sorted(_user_stories, key=lambda x: int(x.title.split(' - ')[0].replace('US', '')))
        return [
            ProjectActivity(self.repository, us, self.reporting_date) for us in _user_stories
        ]

    def dump(self, output_file: Path):
        now = datetime.now()
        report_data = {
            'metadata': {
                'report_date': self.reporting_date.strftime('%Y-%m'),
                'publication_date': self.reporting_date.strftime('%Y-%m-%d')
            },
            'announcements': '',
            'user_stories': []
        }
        for us in self.user_stories:
            us_data = {
                'number': us.number,
                'title': us.title,
                'body': us.body,
                'state': us.state,
                'has_reports': us.has_reports,
                'has_tasks': us.has_tasks,
                'url': us.html_url,
                'tasks': []
            }
            for t in us.tasks:
                us_data['tasks'].append({
                    'number': t.number,
                    'title': t.title,
                    'body': t.body,
                    'state': t.state,
                    'has_reports': t.has_reports,
                    'url': t.html_url,
                })
            report_data['user_stories'].append(us_data)
        with output_file.open('w') as out:
            json.dump(report_data, out, indent=2)

    def generate_report(self, output_file: Path, report_number: str = 'xx'):
        self.user_stories = self.get_user_stories()
        template = self.jinja_env.get_template('report.md.jinja')

        with output_file.open('w') as f:
            f.write(template.render(
                user_stories=self.user_stories,
                report_number=report_number,
                report_date=self.reporting_date.strftime('%Y-%m'),
                publication_date=self.reporting_date.strftime('%Y-%m-%d'),
            ))


if __name__ == '__main__':
    report = ProjectReport()
    # report.generate_report()
