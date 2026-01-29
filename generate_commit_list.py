import os
import sys
from pathlib import Path

from report_generator.commits import dump_commit_list

s = sys.argv[1]
output_dir = Path('./output')
os.makedirs(output_dir, exist_ok=True)
dump_commit_list(output_dir / 'commits.md', s)
print(f'List generated in {output_dir}')
