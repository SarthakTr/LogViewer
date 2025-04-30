import csv
import os
import re

# Define the paths for raw and structured logs (with placeholders for session_id)
LOGS_RAW_TEMPLATE = 'data/raw/logs_{}.txt'
LOGS_STRUCTURED_TEMPLATE = 'data/structured/logs_structured_{}.csv'

# Regular expression for parsing logcat output
log_pattern = re.compile(
    r'(?P<month>0[1-9]|1[0-2])-(?P<day>0[1-9]|[12]\d|3[01])\s+(?P<hour>[01]\d|2[0-4]):(?P<min>[0-5]\d):(?P<sec>[0-5]\d)\.(?P<milsec>\d{3})\s+(?P<pid>\d+)\s+(?P<tid>\d+)\s+(?P<level>[VDIWEFS])\s+(?P<component>.+?)\s*:\s+(?P<content>.*)'
)

def filter_logs_for_display(log_entries, levels=["F", "E", "W"]):
    # Filter out logs that are only in the specified levels
    return [entry for entry in log_entries if entry['Log Level'] in levels]

def parse_logcat(raw_log_path, structured_log_path, filter_for_display=False):
    log_entries = []
    with open(raw_log_path, 'r', encoding='utf-8') as raw_file, \
         open(structured_log_path, 'w', newline='', encoding='utf-8') as csv_file:

        writer = csv.writer(csv_file)
        # Write headers
        writer.writerow(['Month', 'Day', 'Hour', 'Min', 'Sec', 'Milsec', 'PID', 'TID', 'Log Level', 'Component', 'Content'])

        for line in raw_file:
            match = log_pattern.match(line)
            if match:
                entry = {
                    'Month': match.group('month'),
                    'Day': match.group('day'),
                    'Hour': match.group('hour'),
                    'Min': match.group('min'),
                    'Sec': match.group('sec'),
                    'Milsec': match.group('milsec'),
                    'PID': match.group('pid'),
                    'TID': match.group('tid'),
                    'Log Level': match.group('level'),
                    'Component': match.group('component'),
                    'Content': match.group('content')
                }
                log_entries.append(entry)
                writer.writerow(entry.values())

    # Apply filtering if requested
    if filter_for_display:
        log_entries = filter_logs_for_display(log_entries)

    return log_entries

def main(session_id, filter_for_display=False):
    raw_log_path = LOGS_RAW_TEMPLATE.format(session_id)
    structured_log_path = LOGS_STRUCTURED_TEMPLATE.format(session_id)

    # Ensure the raw log file exists
    if os.path.exists(raw_log_path):
        # Parse the log file and write structured output
        return parse_logcat(raw_log_path, structured_log_path, filter_for_display=filter_for_display)
    else:
        print(f"No raw log file found for session {session_id}")
        return []

if __name__ == "__main__":
    import sys
    # Pass session_id and filter_for_display as command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python android.py <session_id> [filter_for_display]")
    else:
        session_id = sys.argv[1]
        filter_for_display = len(sys.argv) > 2 and sys.argv[2] == 'true'
        main(session_id, filter_for_display)
