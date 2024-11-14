# Information about log and how to handle them:
#  - how to parse them
#  - how to parse the date
import re
import datetime
import locale


class LogType:
    """Generic class for log types."""

    pass


class UlogcatLongLogType(LogType):
    """Handle logs from command 'ulogcat -v long'."""

    name = "ulogcat"
    examples = [
        "03-23 15:39:00.412 I SENSORSSVC  (aap-4752/AndroidAutoMsg-5000)   : Activate driver distraction restrictions with mask 0x0",
        "03-23 15:39:00.412 I             (aap-4752/readerThread-6272)     : Phone reported protocol version 1.7",
        "03-23 15:39:00.404 I DISPMAN     (display-focus-m-1577)           : onRequireInputCategory request from 'aap'",
        "03-24 08:39:18.608 I             (debug-logpacka-2055/debug-logpacka-2088): logpackager-ulogcat-stream-plugin: Recording is stopped",
    ]

    regex = re.compile(
        r"^(?P<date>\d\d-\d\d \d\d:\d\d:\d\d.\d\d\d) (?P<level>.) (?P<tag>[^( ]*)\s*\((?:(?P<processname>.*)-(?P<processid>.*)\/)?(?P<threadname>[^\/]*)-(?P<threadid>\d+)\)\s*: ?(?P<content>.*)$"
    )

    date_format = "%m-%d %H:%M:%S.%f"
    date_locale = None


class UlogcatShortLogType(LogType):
    """Handle logs from command 'ulogcat'."""

    name = "ulogcat_short"
    examples = [
        "N boxinit     (boxinit)                        : starting 'sensors-man'",
        "N SENSORS     (sensors-manager)                : Sensor Manager starting (compiled from v42.1.1 on the Jan  2 2023 at 13:43:15)",
        "I BAGADBACK   (sensors-manager)                : notifyConnStatus: Server connected",
    ]
    regex = re.compile(
        r"^(?P<level>.) (?P<tag>[^( ]*)\s*\((?P<processname>[^)]*)\)\s*: ?(?P<content>.*)$"
    )
    date_format = None
    date_locale = None


class LogcatLogType(LogType):
    """Handle logs from command 'logcat'."""

    name = "logcat"
    examples = [
        "03-24 08:36:15.304  4688  5002 D MainThread: Send DriverDistraction: 0",
        "03-24 08:36:15.306  4688  5002 I MainThread: Request type: PopUp",
        "03-24 08:36:15.308  4451  4451 I VehiclePropertyService: onChangeEvent id = 555745548",
        "03-24 08:36:15.308  4451  4451 D VehiclePropertyService: onChangeEvent: property ignored",
    ]

    regex = re.compile(
        r"^(?P<date>\d\d-\d\d \d\d:\d\d:\d\d.\d\d\d)\s+(?P<processid>\d+)\s+(?P<threadid>\d+)\s+(?P<level>.)\s+(?P<tag>[^:]*):(?P<content>.*)$"
    )

    date_format = "%m-%d %H:%M:%S.%f"
    date_locale = None


# Regexp for a dmesg line
DMESG_RE = re.compile(
    r"^(<\d+>)?\[(?P<date>[^]]+)\] (?P<processid>[^:]*:)?(?P<content>.*)$"
)


class DmesgDefaultLogType(LogType):
    """Handle logs at the dmesg format from command 'dmesg'."""

    name = "dmesg"
    examples = [
        "[43189.299397] usb 1-4: new high-speed USB device number 27 using xhci_hcd",
        "[43189.460250] usb 1-4: New USB device strings: Mfr=1, Product=2, SerialNumber=3",
        "[43189.460255] usb 1-4: Product: USB download gadget",
        "[43288.264615] usb 1-4: USB disconnect, device number 27",
        "[    4.849161] hub 3-0:1.0: [INFO][USB] 1 port detected",
        "[   13.118810] p2p is supported",
        "[15537.298409] [UFW BLOCK] IN=wlp0s20f3 OUT= MAC=f4:4e:e3:a8:63:1c:bc:05:df:df:3d:dd:08:00 SRC=192.168.1.30 DST=192.168.1.45 LEN=522 TOS=0x00 PREC=0x00 TTL=64",
    ]
    regex = DMESG_RE
    date_format = None
    date_locale = None


class DmesgHumanTimestampsLogType(LogType):
    """Handle logs at the dmesg format from command 'dmesg -T'."""

    name = "dmesg_humantime"
    examples = [
        "[Fri May 12 15:41:55 2023] CFG80211-INFO) wl_print_event_data : event_type (5), ifidx: 0 bssidx: 0 status:0 reason:7",
        "[Fri May 12 15:41:55 2023] CFG80211-INFO) wl_notify_connect_status_ap : [wlan0] Mode AP/GO. Event:5 status:0 reason:7",
        "[Fri May 12 15:41:55 2023] CFG80211-INFO) wl_notify_connect_status_ap : [wlan0] del sta event for 4e:37:29:ae:b2:0d",
        #        "[jeu. nov.  7 13:16:43 2024] [UFW BLOCK] IN=wlp0s20f3 OUT= MAC=f4:4e:e3:a8:63:1c:bc:05:df:df:3d:dd:08:00 SRC=19",
    ]
    regex = DMESG_RE
    date_format = "%a %b %d %H:%M:%S %Y"
    date_locale = None


class DmesgRawLogType(LogType):
    """Handle logs at the dmesg format from command 'dmesg -r'."""

    name = "dmesg_raw"
    examples = [
        "<6>[  218.824860] CFG80211-INFO) wl_cfg80211_change_station : [wlan_oem0] WLC_SCB_DEAUTHORIZE a6:f9:fc:74:da:e4",
        "<4>[  218.825103] ETHER_TYPE_802_1X[wlan_oem0] [TX]: EAPOL Packet, 4-way handshake, M1 TX_PKTHASH:0x0 TX_PKT_FATE:N/A",
        "<4>[  218.845061] ETHER_TYPE_802_1X[wlan_oem0] [RX]: EAPOL Packet, 4-way handshake, M2",
        "<4>[  218.846470] ETHER_TYPE_802_1X[wlan_oem0] [TX]: EAPOL Packet, 4-way handshake, M3 TX_PKTHASH:0x0 TX_PKT_FATE:N/A",
        "<4>[  218.849981] ETHER_TYPE_802_1X[wlan_oem0] [RX]: EAPOL Packet, 4-way handshake, M4",
        "<4>[15779.293768] [UFW BLOCK] IN=wlp0s20f3 OUT= MAC=f4:4e:e3:a8:63:1c:bc:05:df:df:3d:dd:08:00 SRC=192.168.1.30",
    ]
    regex = DMESG_RE
    date_format = None
    date_locale = None


class JenkinsLogType(LogType):
    """Handle logs from Jenkins."""

    name = "jenkins"
    examples = [
        "[2023-04-20T10:48:36.473Z] TARGET_BUILD_TYPE=release",
        "[2023-04-20T13:46:18.263Z] [ 91% 1805/1973] //external/llvm/lib/Transforms/Vectorize:libLLVMVectorize clang++ BBVectorize.cpp [windows]",
    ]

    regex = re.compile(
        r"^\[(?P<date>[0-9TZ:.-]*)\](?P<progress> \[\s*\d+% \d+/\d+])? ?(?P<content>.*)$"
    )

    date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    date_locale = None


class JournalCtlLogType(LogType):
    """Handle logs from journalctl (RFC5424)."""

    name = "journalctl"
    examples = [
        "juil. 26 16:21:56 hostname.ls.ege.ds tracker-store[2124436]: OK",
        "juil. 26 16:21:56 hostname.ls.ege.ds systemd[4007]: tracker-store.service: Succeeded.",
        "juil. 26 16:23:30 hostname.ls.ege.ds gnome-shell[4356]: Removing a network device that was not added",
        "nov. 06 14:13:43 hostname.ls.ege.ds systemd[4676]: Started Tracker metadata database store and lookup manager.",
        "nov. 06 14:14:13 hostname.ls.ege.ds tracker-store[762255]: OK",
        "nov. 06 14:14:13 hostname.ls.ege.ds systemd[4676]: tracker-store.service: Succeeded.",
    ]
    regex = re.compile(
        r"^(?P<date>.* \d+ \d+:\d+:\d+) (?P<hostname>.*) (?P<processname>.*)\[(?P<processid>\d+)]: (?P<content>.*)$"
    )
    date_format = "%b %d %H:%M:%S"
    date_locale = "fr_FR.UTF-8"


class SysLogLogType(LogType):
    """Handle logs at the syslog format - for example from the command 'sudo cat /var/log/syslog'."""

    name = "syslog"
    examples = [
        "Nov  6 17:10:50 hostname cr-edr-activeprobe 4243 INFO 2024-11-06_16:10:48 ServerPublishBufferSink.cpp.o:211 1 items, PublishService-ServerPublishBufferSink, 168 bytes, Seq 2752",
        "Nov  7 09:06:15 hostname sudo Nov  7 09:06:12 2024 : user : HOST=HOSTNAME : TTY=tty2 ;",
        "Nov  7 09:06:15 hostname kernel: [  752.923011] Lockdown: systemd-logind: hibernation is restricted;7",
        "Nov  6 17:10:53 hostname systemd[4676]: tracker-extract.service: Succeeded.",
        "Nov  6 17:10:53 hostname systemd[1]: Starting Refresh fwupd metadata and update motd...",
        "Nov  6 17:10:53 hostname systemd[1]: fwupd-refresh.service: Succeeded.",
    ]

    regex = re.compile(
        r"^(?P<date>[^ ]* +\d+ \d+:\d+:\d+) (?P<hostname>.*) (?P<content>.*)$"
    )
    date_format = "%b %d %H:%M:%S"
    date_locale = None


class XxxLogType(LogType):
    """Handle logs at the xxx format."""

    name = "xxx"
    examples = []
    regex = re.compile(r"^.*$")
    date_format = None
    date_locale = None


# FORMATS
#########################################
LOG_TYPES = [
    UlogcatLongLogType,
    UlogcatShortLogType,
    LogcatLogType,
    DmesgDefaultLogType,
    DmesgHumanTimestampsLogType,
    DmesgRawLogType,
    JenkinsLogType,
    JournalCtlLogType,
    SysLogLogType,
]


# FORMAT CONFIGURATIONS
#########################################

# Mapping from name of the log format to log information
LOG_CONFIGS = {log_type.name: log_type for log_type in LOG_TYPES}


# ARGPARSE CONFIGURATION
# To be used like this:
#    parser.add_argument("-format", **LOG_CONFIG_ARG)
#########################################
LOG_CONFIG_ARG = {
    "choices": LOG_CONFIGS.keys(),
    "default": "ulogcat",
    "help": "Log format",
}


def get_log_config_from_arg(log_type_name):
    return LOG_CONFIGS[log_type_name]


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
