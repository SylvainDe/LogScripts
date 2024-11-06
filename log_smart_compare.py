"""
This script is used to compare log files which are usually hard to compare for various reasons:
 - some data should not be compared (timestamps, thread identifiers, etc)
 - irrelevant events in the wrong order mess up with the diff
Hence, the script tries to get the relevant data and stores them with a clean format in a well defined file hierarchy.
Then, the output folders can be compared with a proper tool such as meld or kompare.
"""

import sys
import re
import tempfile
import os
import subprocess

from log_types import LOG_TYPES

OUTPUT_FORMATS = {
    # Output format for an ulogcat line
    "ulogcat": "DATE {level} {tag} ({processname}-PID/{threadname}-TID): {clean_content}",
    # Output format for a short ulogcat line
    "ulogcat_short": "{level} {tag} ({processname}): {clean_content}",
    # Output format for a logcat line
    "logcat": "DATE PID TID {level} {tag} {clean_content}",
    # Output format for a dmesg line
    "dmesg": "DATE {processid} {clean_content}",
    "dmesg_humantime": "DATE {processid} {clean_content}",
    "dmesg_raw": "DATE {processid} {clean_content}",
    # Output format for a Jenkins line
    "jenkins": "DATE {content}",
    # Output format for a journalctl line
    "journalctl": "DATE {hostname} {processname} {processid} {clean_content}",
    # Output format for a syslog line
    "syslog": "DATE {hostname} {processname} {clean_content}",
}

# Mapping from name of the log format to log information
LOG_CONFIGS = {
    log_type.name: (log_type, OUTPUT_FORMATS[log_type.name]) for log_type in LOG_TYPES
}


def clean_content(s):
    hex_ign_case = "[0-9a-fA-F]"
    hex_upp_case = "[0-9A-F]"
    hex_low_case = "[0-9a-f]"
    # Replace hex strings (like "0xf0c371cdfcaca")
    s = re.sub("0x{0}+".format(hex_ign_case), "<hex>", s)
    # Replace MAC/Bluetooth addresses (like "F0:C3:71:CD:CA:CA" or "72:5a:7d:6c:26:19")
    s = re.sub(
        "{0}{{2}}:{0}{{2}}:{0}{{2}}:{0}{{2}}:{0}{{2}}:{0}{{2}}".format(hex_ign_case),
        "<mac>",
        s,
    )
    # Replace UUID (like "22A0B758-3FC3-480F-87A0-AECCA283CACA")
    s = re.sub(
        "{0}{{8}}-{0}{{4}}-{0}{{4}}-{0}{{4}}-{0}{{12}}".format(hex_upp_case),
        "<uuid>",
        s,
    )
    # Clean date (like "2008-01-01 12:27:32.963591 AM")
    s = re.sub("\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d+ [AMP]+", "<date>", s)
    # Replace hashcodes (like "@ce7ed73")
    s = re.sub("@{0}+".format(hex_low_case), "<hash>", s)
    return s


def extract_data(f, log_config):
    """Extract relevant data from file - return a dictionnary."""
    log_type, out_format = log_config
    log_re = log_type.regex
    bigdict = dict()
    dict_all = bigdict.setdefault("ALL", dict())
    clean_lst = dict_all.setdefault("clean", [])
    original_lst = dict_all.setdefault("original", [])
    no_match = dict_all.setdefault("nomatch", [])
    for line in f:
        line = line.strip()
        if line:
            m = re.match(log_re, line)
            if m is None:
                no_match.append(line)
            else:
                d = m.groupdict()
                try:
                    d["clean_content"] = clean_content(d["content"])
                except KeyError:
                    pass
                out_line = out_format.format(**d)
                for k, v in d.items():
                    bigdict.setdefault(k, dict()).setdefault(v, []).append(out_line)
                clean_lst.append(out_line)
            original_lst.append(line)
    if no_match:
        log = "%s lines from %s did not match (out of %s):" % (
            len(no_match),
            f.name,
            len(original_lst),
        )
        print(log)
        for line in no_match:
            print("  '" + line + "'")
        print(log)
    return bigdict


def store_relevant_data_in_a_tmp_folder(f, log_config, group_keys):
    """Store relevant data from file provided into a tmp folder."""
    # Extract relevant data from file
    bigdict = extract_data(f, log_config)
    # Store data in multiple files in a temporary folder
    tmpdir = tempfile.mkdtemp()
    print("%s analysed in %s" % (f.name, tmpdir))
    for k in group_keys:
        if k in bigdict:
            newdir = tmpdir + "/" + k
            os.mkdir(newdir)
            for value, lines in bigdict[k].items():
                cleanval = "".join(c if c.isalnum() else "_" for c in str(value))
                newfile = "%s/%s_%s.txt" % (newdir, k, cleanval)
                with open(newfile, "x") as file2:
                    for line in lines:
                        file2.write(line + "\n")
    return tmpdir


def compare_files(files, log_config, group_keys, difftool):
    """Compare files by storing relevant data into a file hierarchy compared by a dedicated tool."""
    # Store relevant data in /tmp folders
    tmpdirs = [
        store_relevant_data_in_a_tmp_folder(f, log_config, group_keys) for f in files
    ]

    # Compare final directories in /tmp
    subprocess.run([difftool] + tmpdirs)


if __name__ == "__main__":
    import argparse

    # Define argparse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "files",
        type=argparse.FileType("r", encoding="ISO-8859-1"),
        nargs="+",
        help="Input files",
    )
    parser.add_argument(
        "-format", choices=LOG_CONFIGS.keys(), default="ulogcat", help="Log format"
    )
    parser.add_argument(
        "-difftool", default="meld", help="Diff tool such as meld or kompare"
    )
    default_group_keys = [
        "tag",
        "threadname",
        "threadid",
        "level",
        "processname",
        "processid",
        "ALL",
    ]
    parser.add_argument(
        "-key",
        action="append",
        help="Keys used to group lines in folders. Unavailable values are ignored. Values available depend on the format used: ALL for all formats, then %s. Default value: %s."
        % (
            ";".join(
                " for %s: %s"
                % (log_type.name, ", ".join(log_type.regex.groupindex.keys()))
                for log_type in LOG_TYPES
            ),
            default_group_keys,
        ),
    )

    # Get arguments
    args = parser.parse_args()
    group_keys = default_group_keys if args.key is None else args.key
    log_config = LOG_CONFIGS[args.format]

    # Perform comparison
    compare_files(args.files, log_config, group_keys, args.difftool)
