import csv
import os
import re
import subprocess

LOGS_RAW_TEMPLATE = 'data/raw/ios_logs_{}.txt'
LOGS_STRUCTURED_TEMPLATE = 'data/structured/ios_logs_structured_{}.csv'

log_pattern = re.compile(
    r'(?P<month>[A-Za-z]{3})\s+(?P<day>\d{2})\s+(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})\s+(?P<device>\S+)\s+(?P<process>.+?)\[(?P<pid>\d+)\]\s+<(?P<level>\w+)>:\s+(?P<content>.*)'
)

def capture_syslog(raw_log_path):
    """Use libimobiledevice's `idevicesyslog` to capture iOS syslogs and save them to a raw log file."""
    with open(raw_log_path, 'w', encoding='utf-8') as raw_file:
        process = subprocess.Popen(['idevicesyslog'], stdout=raw_file, stderr=subprocess.PIPE)
        try:
            process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            process.terminate()

def filter_logs_for_display(log_entries, levels=["F", "E", "W"]):
    """Filter logs to include only entries with specified log levels."""
    return [entry for entry in log_entries if entry['Log Level'] in levels]

def parse_syslog(raw_log_path, structured_log_path, filter_for_display=False):
    log_entries = []
    with open(raw_log_path, 'r', encoding='utf-8') as raw_file, \
         open(structured_log_path, 'w', newline='', encoding='utf-8') as csv_file:
        
        writer = csv.writer(csv_file)
        writer.writerow(['Month', 'Day', 'Hour', 'Min', 'Sec', 'Device', 'Process', 'PID', 'Content'])

        for line in raw_file:
            match = log_pattern.match(line)
            if match:
                entry = {
                    'Month': match.group('month'),
                    'Day': match.group('day'),
                    'Hour': match.group('hour'),
                    'Min': match.group('min'),
                    'Sec': match.group('sec'),
                    'Device': match.group('device'),
                    'Process': match.group('process'),
                    'PID': match.group('pid'),
                    'Content': match.group('content')
                }
                log_entries.append(entry)
                writer.writerow(entry.values())

    if filter_for_display:
        log_entries = filter_logs_for_display(log_entries)

    return log_entries

def main(session_id, filter_for_display=False):
    raw_log_path = LOGS_RAW_TEMPLATE.format(session_id)
    structured_log_path = LOGS_STRUCTURED_TEMPLATE.format(session_id)

    capture_syslog(raw_log_path)

    if os.path.exists(raw_log_path):
        return parse_syslog(raw_log_path, structured_log_path, filter_for_display=filter_for_display)
    else:
        print(f"No raw log file found for session {session_id}")
        return []

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python ios.py <session_id> [filter_for_display]")
    else:
        session_id = sys.argv[1]
        filter_for_display = len(sys.argv) > 2 and sys.argv[2] == 'true'
        main(session_id, filter_for_display)
