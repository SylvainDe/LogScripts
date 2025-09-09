"""
This script is used to compute delta time/time differences between line
of logs as it can make things easier to understand sometimes.
"""
import re
import datetime
from log_types import (
    LOG_CONFIG_ARG,
    get_log_config_from_arg,
)


def get_timed_lines(input_file, log_type):
    log_re, date_format = log_type.regex, log_type.date_format
    no_match = list()
    lines = list(input_file)
    for line in lines:
        line = line.strip()
        if line:
            m = re.match(log_re, line)
            if m is None:
                no_match.append(line)
            else:
                d = datetime.datetime.strptime(m.groupdict()["date"], date_format)
                yield d, line
    if no_match:
        log = "%s lines from %s did not match (out of %s):" % (
            len(no_match),
            input_file.name,
            len(lines),
        )
        print(log)
        for line in no_match:
            print("  '" + line + "'")
        print(log)


def get_ms(td):
    return "" if td is None else int(td / datetime.timedelta(milliseconds=1))


def process_file(input_file, log_type, diff_type, matching, output_format):
    timed_lines = list(get_timed_lines(input_file, log_type))
    matching_compiled = re.compile(matching)
    abs_time = None
    if diff_type in ("first", "last"):
        matches = [d for d, line in timed_lines if re.search(matching_compiled, line)]
        if not matches:
            print("No match for", matching, "in the", len(timed_lines), "lines")
            return
        abs_time = matches[0 if diff_type == "first" else -1]

    prev_d = None
    for d, line in timed_lines:
        if abs_time is not None:
            diff = d - abs_time
        else:
            diff = None if prev_d is None else (d - prev_d)
            if re.search(matching_compiled, line):
                prev_d = d
        print(output_format.format(get_ms(diff), line))


if __name__ == "__main__":
    import argparse

    # Define argparse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file",
        type=argparse.FileType("r", encoding="ISO-8859-1"),
        help="Input file",
    )
    parser.add_argument("-format", **LOG_CONFIG_ARG)
    parser.add_argument(
        "-diff",
        choices=["first", "last", "next"],
        default="first",
        help="Difference type",
    )
    parser.add_argument("-matching", default="", help="Matching")
    output_format = "[{0:>8} ms] {1}"
    parser.add_argument(
        "-outputformat",
        default=output_format,
        help='Output format ({{0}} is the delta time and {{1}} is the original log line). Defaults to "{0}"'.format(
            output_format
        ),
    )

    # Get arguments
    args = parser.parse_args()
    print(args)
    input_file = args.file
    log_type = get_log_config_from_arg(args.format, [input_file])
    process_file(input_file, log_type, args.diff, args.matching, args.outputformat)
