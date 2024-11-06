"""
This script is used to find the first and last logs for a given process or
thread.
"""

import sys
import re
import tempfile
import os
import subprocess
from log_types import LOG_CONFIGS


def process_file(f, log_re):
	no_match = list()
    # TODO: This part should be different based on the log type
	key_format="{processid}/{threadid}"
	lines_by_key=dict()

	for line in f:
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
		print("%d lines did not match regexp", len(no_match))

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
    parser.add_argument(
        "-format", choices=LOG_CONFIGS.keys(), default="ulogcat", help="Log format"
    )

    # Get arguments
    args = parser.parse_args()
    log_re = LOG_CONFIGS[args.format].regex

    # Do process
    process_file(args.file, log_re)
