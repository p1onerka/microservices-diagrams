import csv
import sys

csv_file = sys.argv[1]
values = sys.argv[2:]
with open(csv_file, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(values)
