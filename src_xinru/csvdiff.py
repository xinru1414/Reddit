import csv
import sys

key = sys.argv[1]
file1 = sys.argv[2]
file2 = sys.argv[3]


seenkeys = {row[key] for row in csv.DictReader(open(file1))}

rdr2 = csv.DictReader(open(file2))
out = csv.writer(sys.stdout)
out.writerow(rdr2.fieldnames)
for row in rdr2:
    if row[key] not in seenkeys:
        out.writerow([row[f] for f in rdr2.fieldnames])


