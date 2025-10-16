"""
This script is used to find the first and last logs for a given process or
thread.
"""

import sys
import re
import tempfile
import os
import subprocess
from log_types import (
    LOG_TYPES,
    LOG_CONFIG_ARG,
    get_log_config_from_arg,
    UlogcatLongLogType,
    UlogcatShortLogType,
    LogcatLogType,
    DmesgDefaultLogType,
    DmesgHumanTimestampsLogType,
    DmesgRawLogType,
    JenkinsLogType,
    JournalCtlLogType,
    SysLogLogType,
    ZazuSocLogType,
)


# Add information about the key format to the log types
UlogcatLongLogType.key_format = "{processid}/{threadid}"
UlogcatShortLogType.key_format = "{processid}"
ZazuSocLogType.key_format = "{processname}"
LogcatLogType.key_format = "{processid}/{threadid}"
DmesgDefaultLogType.key_format = "NO KEY DEFINED"
DmesgHumanTimestampsLogType.key_format = "NO KEY DEFINED"
DmesgRawLogType.key_format = "NO KEY DEFINED"
JenkinsLogType.key_format = "{processid}"
JournalCtlLogType.key_format = "{processid}"
SysLogLogType.key_format = "NO KEY DEFINED"


def process_file(input_file, log_type):
    log_re = log_type.regex
    key_format = log_type.key_format
    no_match = list()
    lines_by_key = dict()
    lines = list(input_file)
    for line in lines:
        line = line.strip()
        if line:
            m = re.match(log_re, line)
            if m is None:
                no_match.append(line)
            else:
                d = m.groupdict()
                key_str = key_format.format(**d)
                lines_by_key.setdefault(key_str, []).append(line)
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

    for k, v_lst in lines_by_key.items():
        print()
        print(k, len(v_lst))
        print(v_lst[0])
        if len(v_lst) > 1:
            print(v_lst[-1])


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

    # Get arguments
    args = parser.parse_args()
    input_file = args.file
    log_type = get_log_config_from_arg(args.format, [input_file])

    # Do process
    process_file(input_file, log_type)
