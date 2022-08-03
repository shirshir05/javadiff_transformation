import csv

try:
    from javadiff.FileDiff import FileDiff
except:
    from javadiff.javadiff.diff import FileDiff

import sys

from diff import get_commit_diff

if __name__ == "__main__":

    m = get_commit_diff(r"C:\temp\commons-collections", 'eef8f1a0aa2bc6083dc5d0ed5458c830816c5bad', analyze_diff=True)
    m.get_metrics()
    print("s")