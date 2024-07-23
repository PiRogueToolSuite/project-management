import os
import sys
from pathlib import Path
from datetime import datetime

import jinja2

from report_generator.report import ProjectReport

# jinja_env = jinja2.Environment(loader=jinja2.PackageLoader('report_generator', './templates/'))
# jinja_env.get_template('report.md.jinja')
# sys.exit(0)

now = datetime.now()
output_dir = Path('./output')
report_date = now.strftime('%Y-%m')
report_number = sys.argv[1] if len(sys.argv) > 1 else 'xx'
report_dir = output_dir / f'Monthly report #{report_number} - {report_date}'
escaped_report_dir = Path(str(report_dir).replace(' ', '\ '))
# report_url = f'http://localhost:1313/blog/monthly-report-n{report_number}-{report_date}/'
report_url = f'https://pts-project.org/blog/monthly-report-n{report_number}-{report_date}/'

# Create the report directory if it doesn't exist
os.makedirs(report_dir, exist_ok=True)
# generator = ProjectReport()
# generator.generate_report(report_dir / 'index.md', report_number)
# generator.dump(report_dir / 'report.json')
print(f'Report generated at {report_dir}')
print('Publish the monthly report on the website')
print('Once published, generate additional versions of the report')
print(f' curl -o {escaped_report_dir / "email.html"} {report_url}email.html')
print(f' wkhtmltopdf --encoding utf-8 {escaped_report_dir / "email.html"} {escaped_report_dir / "report.pdf"}')
print(f'Email subject: \n PiRogue Tool Suite - Monthly report #{report_number} {report_date}')
print(f'Email subject: \n PiRogue Tool Suite - Monthly report')
