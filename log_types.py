# Information about log and how to handle them:
#  - how to parse them
#  - how to parse the date
import re
import datetime
import locale
from collections import namedtuple

LogType = namedtuple(
    "LogType",
    [
        "name",
        "regex",
        "date_format",
        "date_locale",
        "examples",
    ],
)

# ULOGCAT FORMAT
#########################################
# Examples:
# for command 'ulogcat -v long'
ULOGCAT_EXAMPLES = [
    "03-23 15:39:00.412 I SENSORSSVC  (aap-4752/AndroidAutoMsg-5000)   : Activate driver distraction restrictions with mask 0x0",
    "03-23 15:39:00.412 I             (aap-4752/readerThread-6272)     : Phone reported protocol version 1.7",
    "03-23 15:39:00.404 I DISPMAN     (display-focus-m-1577)           : onRequireInputCategory request from 'aap'",
    "03-24 08:39:18.608 I             (debug-logpacka-2055/debug-logpacka-2088): logpackager-ulogcat-stream-plugin: Recording is stopped",
]

# Regexp for an ulogcat line
ULOGCAT_RE = re.compile(
    r"^(?P<date>\d\d-\d\d \d\d:\d\d:\d\d.\d\d\d) (?P<level>.) (?P<tag>[^( ]*)\s*\((?:(?P<processname>.*)-(?P<processid>.*)\/)?(?P<threadname>[^\/]*)-(?P<threadid>\d+)\)\s*: ?(?P<content>.*)$"
)

# Date format for an ulogcat date
ULOGCAT_DATE_FORMAT = "%m-%d %H:%M:%S.%f"

# Output format for an ulogcat line
ULOGCAT_OUTPUT_FORMAT = (
    "DATE {level} {tag} ({processname}-PID/{threadname}-TID): {clean_content}"
)

# Tuple with all information
ULOGCAT_LOG_TYPE = LogType(
    name="ulogcat",
    regex=ULOGCAT_RE,
    date_format=ULOGCAT_DATE_FORMAT,
    date_locale=None,
    examples=ULOGCAT_EXAMPLES,
)

# ULOGCAT SHORT FORMAT
#########################################
# Examples:
# for command 'ulogcat'
ULOGCAT_SHORT_EXAMPLES = [
    "N boxinit     (boxinit)                        : starting 'sensors-man'",
    "N SENSORS     (sensors-manager)                : Sensor Manager starting (compiled from v42.1.1 on the Jan  2 2023 at 13:43:15)",
    "I BAGADBACK   (sensors-manager)                : notifyConnStatus: Server connected",
]

# Regexp for an ulogcat line
ULOGCAT_SHORT_RE = re.compile(
    r"^(?P<level>.) (?P<tag>[^( ]*)\s*\((?P<processname>[^)]*)\)\s*: ?(?P<content>.*)$"
)

# Output format for a short ulogcat line
ULOGCAT_SHORT_OUTPUT_FORMAT = "{level} {tag} ({processname}): {clean_content}"

# Tuple with all information
ULOGCAT_SHORT_LOG_TYPE = LogType(
    name="ulogcat_short",
    regex=ULOGCAT_SHORT_RE,
    date_format=None,
    date_locale=None,
    examples=ULOGCAT_SHORT_EXAMPLES,
)

# LOGCAT FORMAT
#########################################
# Examples:
LOGCAT_EXAMPLES = [
    "03-24 08:36:15.304  4688  5002 D MainThread: Send DriverDistraction: 0",
    "03-24 08:36:15.306  4688  5002 I MainThread: Request type: PopUp",
    "03-24 08:36:15.308  4451  4451 I VehiclePropertyService: onChangeEvent id = 555745548",
    "03-24 08:36:15.308  4451  4451 D VehiclePropertyService: onChangeEvent: property ignored",
]

# Regexp for a logcat line
LOGCAT_RE = re.compile(
    r"^(?P<date>\d\d-\d\d \d\d:\d\d:\d\d.\d\d\d)\s+(?P<processid>\d+)\s+(?P<threadid>\d+)\s+(?P<level>.)\s+(?P<tag>[^:]*):(?P<content>.*)$"
)

# Date format for an logcat date
LOGCAT_DATE_FORMAT = "%m-%d %H:%M:%S.%f"

# Output format for a logcat line
LOGCAT_OUTPUT_FORMAT = "DATE PID TID {level} {tag} {clean_content}"

# Tuple with all information
LOGCAT_LOG_TYPE = LogType(
    name="logcat",
    regex=LOGCAT_RE,
    date_format=LOGCAT_DATE_FORMAT,
    date_locale=None,
    examples=LOGCAT_EXAMPLES,
)

# DMESG FORMAT
#########################################
# Examples:
# - dmesg
DMESG_EXAMPLES = [
    "[43189.299397] usb 1-4: new high-speed USB device number 27 using xhci_hcd",
    "[43189.460250] usb 1-4: New USB device strings: Mfr=1, Product=2, SerialNumber=3",
    "[43189.460255] usb 1-4: Product: USB download gadget",
    "[43288.264615] usb 1-4: USB disconnect, device number 27",
    "[    4.849161] hub 3-0:1.0: [INFO][USB] 1 port detected",
    "[   13.118810] p2p is supported",
]
# or
DMESG_HUMANTIMESTAMP_EXAMPLES = [
    # - dmesg -T
    "[Fri May 12 15:41:55 2023] CFG80211-INFO) wl_print_event_data : event_type (5), ifidx: 0 bssidx: 0 status:0 reason:7",
    "[Fri May 12 15:41:55 2023] CFG80211-INFO) wl_notify_connect_status_ap : [wlan0] Mode AP/GO. Event:5 status:0 reason:7",
    "[Fri May 12 15:41:55 2023] CFG80211-INFO) wl_notify_connect_status_ap : [wlan0] del sta event for 4e:37:29:ae:b2:0d",
]
# or
# - dmesg -r
DMESG_RAW_EXAMPLES = [
    "<6>[  218.824860] CFG80211-INFO) wl_cfg80211_change_station : [wlan_oem0] WLC_SCB_DEAUTHORIZE a6:f9:fc:74:da:e4",
    "<4>[  218.825103] ETHER_TYPE_802_1X[wlan_oem0] [TX]: EAPOL Packet, 4-way handshake, M1 TX_PKTHASH:0x0 TX_PKT_FATE:N/A",
    "<4>[  218.845061] ETHER_TYPE_802_1X[wlan_oem0] [RX]: EAPOL Packet, 4-way handshake, M2",
    "<4>[  218.846470] ETHER_TYPE_802_1X[wlan_oem0] [TX]: EAPOL Packet, 4-way handshake, M3 TX_PKTHASH:0x0 TX_PKT_FATE:N/A",
    "<4>[  218.849981] ETHER_TYPE_802_1X[wlan_oem0] [RX]: EAPOL Packet, 4-way handshake, M4",
]

# Regexp for a dmesg line
DMESG_RE = re.compile(
    r"^(<\d+>)?\[(?P<date>[^]]+)\] (?P<processid>[^:]*:)?(?P<content>.*)$"
)

# Date format for an dmesg date
DMESG_DATE_FORMAT = None

# Date format for an dmesg with human timestamp date
DMESG_HUMANTIMESTAMP_DATE_FORMAT = "%a %b %d %H:%M:%S %Y"

# Output format for a dmesg line
DMESG_OUTPUT_FORMAT = "DATE {processid} {content}"

# Tuples with all information
DMESG_LOG_TYPE = LogType(
    name="dmesg",
    regex=DMESG_RE,
    date_format=DMESG_DATE_FORMAT,
    date_locale=None,
    examples=DMESG_EXAMPLES,
)

DMESG_HUMANTIMESTAMP_LOG_TYPE = LogType(
    name="dmesg_humantime",
    regex=DMESG_RE,
    date_format=DMESG_HUMANTIMESTAMP_DATE_FORMAT,
    date_locale=None,
    examples=DMESG_HUMANTIMESTAMP_EXAMPLES,
)

DMESG_RAW_LOG_TYPE = LogType(
    name="dmesg_raw",
    regex=DMESG_RE,
    date_format=DMESG_DATE_FORMAT,
    date_locale=None,
    examples=DMESG_RAW_EXAMPLES,
)


# JENKINS FORMAT
#########################################
# Examples:
JENKINS_EXAMPLES = [
    "[2023-04-20T10:48:36.473Z] TARGET_BUILD_TYPE=release",
    "[2023-04-20T13:46:18.263Z] [ 91% 1805/1973] //external/llvm/lib/Transforms/Vectorize:libLLVMVectorize clang++ BBVectorize.cpp [windows]",
]

# Regexp for a Jenkins line
JENKINS_RE = re.compile(
    r"^\[(?P<date>[0-9TZ:.-]*)\](?P<progress> \[\s*\d+% \d+/\d+])? ?(?P<content>.*)$"
)

# Date format for an Jenkins date
JENKINS_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

# Output format for a Jenkins line
JENKINS_OUTPUT_FORMAT = "DATE {content}"

# Tuple with all information
JENKINS_LOG_TYPE = LogType(
    name="jenkins",
    regex=JENKINS_RE,
    date_format=JENKINS_DATE_FORMAT,
    date_locale=None,
    examples=JENKINS_EXAMPLES,
)

# JOURNALCTL FORMAT
# RFC5424
#########################################
# Examples:
JOURNALCTL_EXAMPLES = [
    "juil. 26 16:21:56 hostname.ls.ege.ds tracker-store[2124436]: OK",
    "juil. 26 16:21:56 hostname.ls.ege.ds systemd[4007]: tracker-store.service: Succeeded.",
    "juil. 26 16:23:30 hostname.ls.ege.ds gnome-shell[4356]: Removing a network device that was not added",
    "nov. 06 14:13:43 hostname.ls.ege.ds systemd[4676]: Started Tracker metadata database store and lookup manager.",
    "nov. 06 14:14:13 hostname.ls.ege.ds tracker-store[762255]: OK",
    "nov. 06 14:14:13 hostname.ls.ege.ds systemd[4676]: tracker-store.service: Succeeded.",
]

# Regexp for a journalctl line
JOURNALCTL_RE = re.compile(
    r"^(?P<date>.* \d+ \d+:\d+:\d+) (?P<hostname>.*) (?P<processname>.*)\[(?P<processid>\d+)]: (?P<content>.*)$"
)

# Date format for an journalctl date
JOURNALCTL_DATE_FORMAT = "%b %d %H:%M:%S"

# Output format for a journalctl line
JOURNALCTL_OUTPUT_FORMAT = "DATE {content}"

# Tuple with all information
JOURNALCTL_LOG_TYPE = LogType(
    name="journalctl",
    regex=JOURNALCTL_RE,
    date_format=JOURNALCTL_DATE_FORMAT,
    date_locale="fr_FR.UTF-8",
    examples=JOURNALCTL_EXAMPLES,
)

# SYSLOG FORMAT
#########################################
# Examples:
# sudo cat /var/log/syslog
SYSLOG_EXAMPLES = [
    #     "Nov  6 17:10:50 hostname cr-edr-activeprobe 4243 INFO 2024-11-06_16:10:48 ServerPublishBufferSink.cpp.o:211 1 items, PublishService-ServerPublishBufferSink, 168 bytes, Seq 2752",
    "Nov  6 17:10:53 hostname systemd[4676]: tracker-extract.service: Succeeded.",
    "Nov  6 17:10:53 hostname systemd[1]: Starting Refresh fwupd metadata and update motd...",
    "Nov  6 17:10:53 hostname systemd[1]: fwupd-refresh.service: Succeeded.",
]

# Regexp for a syslog line
SYSLOG_RE = re.compile(
    r"^(?P<date>.* \d+ \d+:\d+:\d+) (?P<hostname>.*) (?P<processname>.*)\[(?P<processid>\d+)]: (?P<content>.*)$"
)

# Date format for an syslog date
SYSLOG_DATE_FORMAT = "%b %d %H:%M:%S"

# Output format for a syslog line
SYSLOG_OUTPUT_FORMAT = "DATE {content}"

# Tuple with all information
SYSLOG_LOG_TYPE = LogType(
    name="syslog",
    regex=SYSLOG_RE,
    date_format=SYSLOG_DATE_FORMAT,
    date_locale=None,
    examples=SYSLOG_EXAMPLES,
)


# XXX FORMAT
#########################################
# Examples:
XXX_EXAMPLES = []

# Regexp for a xxx line
XXX_RE = re.compile(r"^.*$")

# Date format for an xxx date
XXX_DATE_FORMAT = None

# Output format for a xxx line
XXX_OUTPUT_FORMAT = "DATE {content}"

# Tuple with all information
XXX_LOG_TYPE = LogType(
    name="xxx",
    regex=XXX_RE,
    date_format=XXX_DATE_FORMAT,
    date_locale=None,
    examples=XXX_EXAMPLES,
)


# FORMATS
#########################################
LOG_TYPES = [
    ULOGCAT_LOG_TYPE,
    ULOGCAT_SHORT_LOG_TYPE,
    LOGCAT_LOG_TYPE,
    DMESG_LOG_TYPE,
    DMESG_HUMANTIMESTAMP_LOG_TYPE,
    DMESG_RAW_LOG_TYPE,
    JENKINS_LOG_TYPE,
    JOURNALCTL_LOG_TYPE,
    SYSLOG_LOG_TYPE,
]

# FORMAT CONFIGURATIONS
#########################################

# Mapping from name of the log format to log information
LOG_CONFIGS = {log_type.name: log_type for log_type in LOG_TYPES}


# TESTS
#########################################
def test_log_type_for_examples(log_type):
    print(log_type.name)
    log_re = log_type.regex
    date_format = log_type.date_format
    local = log_type.date_locale
    # Save original locale
    prev_locale = locale.setlocale(locale.LC_ALL)
    # Use relevant locale
    if local != prev_locale:
        locale.setlocale(locale.LC_ALL, local)
    for s in log_type.examples:
        m = re.match(log_re, s)
        assert m
        match_dict = m.groupdict()
        date_str = match_dict.get("date")
        if date_format is not None:
            date_obj = datetime.datetime.strptime(date_str, date_format)
            date_str2 = date_obj.strftime(date_format)
            # if date_str != date_str2:
            #     print(date_str, "!=", date_str2)
    # Restore original locale
    if local != prev_locale:
        locale.setlocale(locale.LC_ALL, prev_locale)


if __name__ == "__main__":
    for log_type in LOG_TYPES:
        test_log_type_for_examples(log_type)
