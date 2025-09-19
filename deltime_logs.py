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


def get_timed_lines(input_file, log_re, date_format):
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


def process_file(input_file, log_type, ref_type, reference, delta, output_format):
    log_re, date_format = log_type.regex, log_type.date_format
    timed_lines = list(get_timed_lines(input_file, log_re, date_format))
    abs_time = None
    if ref_type == "absolute":
        abs_time = datetime.datetime.strptime(reference, date_format)
    elif ref_type in ("first", "last"):
        reference_compiled = re.compile(reference)
        matches = [d for d, line in timed_lines if re.search(reference_compiled, line)]
        if not matches:
            print("No match for", reference, "in the", len(timed_lines), "lines")
            return
        abs_time = matches[0 if ref_type == "first" else -1]
    else:
        assert ref_type == "prev"
        reference_compiled = re.compile(reference)

    prev_d = None
    for d, line in timed_lines:
        if abs_time is not None:
            diff = d - abs_time
        else:
            diff = None if prev_d is None else (d - prev_d)
            if re.search(reference_compiled, line):
                prev_d = d
        print(output_format.format(get_ms(diff + delta), line))


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
        "-ref-type",
        choices=["absolute", "first", "last", "prev"],
        default="first",
        help="""Type of time reference:
 - absolute: use time provided (should match input file date format)
 - first: use time from the first line matching the reference param
 - last: use time from the last line matching the reference param
 - prev: use time from the prev line matching the reference param""",
    )
    parser.add_argument("-reference", default="", help="Reference")
    parser.add_argument("-delta", default=0, help="Delta (in ms) which is assigned to reference", type=int)
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
    delta = datetime.timedelta(milliseconds = args.delta)
    process_file(input_file, log_type, args.ref_type, args.reference, delta, args.outputformat)
