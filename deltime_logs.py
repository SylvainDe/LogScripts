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


def get_timed_lines(input_file, log_re, date_obj_from_str):
    no_match = list()
    lines = list(input_file)
    for line in lines:
        line = line.strip()
        if line:
            m = re.match(log_re, line)
            if m is None:
                no_match.append(line)
            else:
                d = date_obj_from_str(m.groupdict()["date"])
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


def get_ms(td, delta):
    if td is None:
        return ""
    return int((td + delta) / datetime.timedelta(milliseconds=1))


def get_diff_from_abs_time(timed_lines, abs_time):
    for d, line in timed_lines:
        diff = d - abs_time
        yield diff, line


def get_diff_from_rel_time(timed_lines, re_ref):
    prev_d = None
    for d, line in timed_lines:
        diff = None if prev_d is None else (d - prev_d)
        if re.search(re_ref, line):
            prev_d = d
        yield diff, line


def process_file(input_file, log_type, ref_type, reference, delta, output_format):
    log_re, date_obj_from_str = log_type.regex, log_type.date_obj_from_str
    timed_lines = list(get_timed_lines(input_file, log_re, date_obj_from_str))
    do_reverse = ref_type in ("last", "next")
    if do_reverse:
        timed_lines = list(reversed(timed_lines))
    abs_time = None
    if ref_type == "absolute":
        abs_time = date_obj_from_str(reference)
        lines_with_diff = list(get_diff_from_abs_time(timed_lines, abs_time))
    elif ref_type in ("first", "last"):
        reference_compiled = re.compile(reference)
        matches = [d for d, line in timed_lines if re.search(reference_compiled, line)]
        if not matches:
            print("No match for", reference, "in the", len(timed_lines), "lines")
            return
        abs_time = matches[0]
        lines_with_diff = list(get_diff_from_abs_time(timed_lines, abs_time))
    elif ref_type in ("prev", "next"):
        reference_compiled = re.compile(reference)
        lines_with_diff = list(get_diff_from_rel_time(timed_lines, reference_compiled))
    else:
        assert False
    if do_reverse:
        lines_with_diff = reversed(lines_with_diff)
    for diff, line in lines_with_diff:
        print(output_format.format(get_ms(diff, delta), line))


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
        choices=["absolute", "first", "last", "prev", "next"],
        default="first",
        help="""Type of time reference:
 - absolute: use time provided (should match input file date format)
 - first: use time from the first line matching the reference param
 - last: use time from the last line matching the reference param
 - prev: use time from the prev line matching the reference param
 - next: use time from the next line matching the reference param""",
    )
    parser.add_argument("-reference", default="", help="Reference")
    parser.add_argument(
        "-delta",
        default=0,
        help="Delta (in ms) which is assigned to reference",
        type=int,
    )
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
    delta = datetime.timedelta(milliseconds=args.delta)
    process_file(
        input_file, log_type, args.ref_type, args.reference, delta, args.outputformat
    )
