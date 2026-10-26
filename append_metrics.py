"""
Append one row of experiment metrics to a CSV file.

Called from opencode_exp.sh after each agent run:

    python3 append_metrics.py <csv_file> <value> [<value> ...]

Every argument after the file path becomes one cell of the new row.
"""

import csv
import sys

csv_file = sys.argv[1]
values = sys.argv[2:]
with open(csv_file, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(values)
