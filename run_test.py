# from simple_ballot import ballot

# INPUT_FILE = r".\test\applicants.csv"

# output = ballot.run_draw(input_path=INPUT_FILE, total_resource=30, ignore_duplicates=False)

import getopt
import sys
import io

try:
    opts, args = getopt.getopt(
        sys.argv[1:],
        "h1o:s:F:A:f:",
        ["help", "header", "output", "sep=", "float=", "align=", "format="],
    )
except getopt.GetoptError as e:
    print(e)
    print(usage)
    sys.exit(2)

files = [sys.stdin] if not args else args


input(getopt.getopt(
    sys.argv[1:],
    "h1o:s:F:A:f:",
    ["help", "header", "output", "sep=", "float=", "align=", "format="],
))
for opt, value in opts:
    print(opt)
input(args)
input(files)
