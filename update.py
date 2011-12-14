# /usr/bin/env python3
# encoding: utf-8

import sys
import os
import re
import datetime
import csv
import urllib.request


LISTFILE = "list.txt"
ICSDIR = "ics"
CSVDIR = "csv"


def icspath(id_):
    return os.path.join(ICSDIR, id_)


def csvpath(id_):
    return os.path.join(CSVDIR, id_)


# [date, summary]
def readics(id_):
    rows = []
    date = None
    summary = None
    for line in open(icspath(id_)):
        line = line.rstrip("\r\n")
        if line == "BEGIN:VEVENT":
            pass
        elif line.startswith("DTSTART;"):
            m = re.match("^DTSTART;VALUE=DATE:(\d{4}\d{2}\d{2})$", line)
            date = datetime.datetime.strptime(m.group(1), "%Y%m%d").date()
        elif line.startswith("SUMMARY:"):
            m = re.match("^SUMMARY:(.*)$", line)
            summary = m.group(1)
        elif line == "END:VEVENT":
            rows.append((date, summary))
    return rows


# [date, summary]
def readcsv(id_):
    rows = []
    for datestr, summary in csv.reader(open(csvpath(id_), newline="")):
        date = datetime.datetime.strptime(datestr, "%Y-%m-%d").date()
        rows.append((date, summary))
    return rows


def writecsv(id_, rows):
    o = open(csvpath(id_), "w")
    writer = csv.writer(o)
    for date, summary in rows:
        writer.writerow([date.strftime("%Y-%m-%d"), summary])
    o.close()


# [id, url, country, title]
def readlist():
    return csv.reader(open(LISTFILE, newline=""))


def mergeicscsv(id_):
    if not os.path.exists(csvpath(id_)):
        rows = readics(id_)
    else:
        year = datetime.datetime.now().year
        rows = []
        for date, summary in readcsv(id_):
            if year < date.year:
                rows.append((date, summary))
        for date, summary in readics(id_):
            if year >= date.year:
                rows.append((date, summary))
    return sorted(rows, key=lambda x: x[0])


def download():
    rows = list(readlist())
    for i, [id_, url, country, title] in enumerate(rows, start=1):
        print("({}/{}): {}".format(i, len(rows), url))
        f = urllib.request.urlopen(url)
        ics = f.read()
        f.close()
        if not ics.startswith(b"BEGIN:VCALENDAR"):
            raise Exception("not ics")
        o = open(icspath(id_), "wb")
        o.write(ics)
        o.close()


def convert():
    for id_, url, country, title  in readlist():
        writecsv(id_, mergeicscsv(id_))


def main():
    download()
    convert()


if __name__ == "__main__":
    sys.exit(main())
