"""
This script is used to compute delta time/time differences between line
of logs as it can make things easier to understand sometimes.
"""
import re
import datetime
from log_types import LOG_CONFIGS

def get_timed_lines(input_file, log_type):
    log_re, date_format = log_type.regex, log_type.date_format
    for line in input_file:
        line = line.strip()
        if line:
            m = re.match(log_re, line)
            if m is not None:
                d = datetime.datetime.strptime(m.groupdict()['date'], date_format)
                yield d, line


def format_timedelta(td):
    if td is None:
        return '-' * 8
    return str(int(td / datetime.timedelta(milliseconds=1))).rjust(8)


def process_file(input_file, log_type, diff_type, matching):
    timed_lines = list(get_timed_lines(input_file, log_type))
    matching_compiled = re.compile(matching)
    abs_time = None
    if diff_type in ('first', 'last'):
        matches = [d for d, line in timed_lines if re.search(matching_compiled, line)]
        if not matches:
            print("No match for", matching, "in the", len(timed_lines), "lines")
            return
        abs_time = matches[0 if diff_type == 'first' else -1]

    prev_d = None
    for d, line in timed_lines:
        if abs_time is not None:
            diff = d - abs_time
        else:
            diff = None if prev_d is None else (d - prev_d)
            if re.search(matching_compiled, line):
                prev_d = d
        print(format_timedelta(diff), line)


if __name__ == "__main__":
    import argparse

    # Define argparse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file",
        type=argparse.FileType("r", encoding="ISO-8859-1"),
        help="Input file",
    )
    parser.add_argument(
        "-format", choices=LOG_CONFIGS.keys(), default="ulogcat", help="Log format"
    )
    parser.add_argument(
        "-diff", choices="first last next", default="first", help="Difference type"
    )
    parser.add_argument(
        "-matching", default="", help="Matching"
    )

    # Get arguments
    args = parser.parse_args()
    log_type = LOG_CONFIGS[args.format]
    process_file(args.file, log_type, args.diff, args.matching)
