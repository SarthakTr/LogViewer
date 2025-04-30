import os
import io
import uuid
import subprocess
import threading
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, timedelta
import shutil
import schedule
import time


LOGS_RAW_DIR = 'data/raw'
LOGS_STRUCTURED_DIR = 'data/structured'

logcat_process = None
logcat_output = io.StringIO()
logcat_thread = None
active_sessions = {}
saved_sessions = {}

ios_process = None
ios_output = io.StringIO()
ios_thread = None

def generate_session_id():
    session_id = str(uuid.uuid4())
    raw_log_path = os.path.join(LOGS_RAW_DIR, f'logs_{session_id}.txt')
    structured_log_path = os.path.join(LOGS_STRUCTURED_DIR, f'logs_structured_{session_id}.csv')
    return session_id, raw_log_path, structured_log_path

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global logcat_process, logcat_output, logcat_thread, ios_process, ios_output, ios_thread
        if self.path.startswith('/android/start'):
            session_id, raw_log_path, structured_log_path = generate_session_id()
            active_sessions[session_id] = datetime.now()
            saved_sessions[session_id] = active_sessions[session_id]

            if logcat_process is None:
                logcat_output = io.StringIO()
                logcat_process = subprocess.Popen(['adb', 'logcat'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                logcat_thread = threading.Thread(target=self.capture_logcat_output, args=(logcat_process, logcat_output, raw_log_path))
                logcat_thread.start()
                response_message = json.dumps({"message": "Logcat started", "session_id": session_id})
            else:
                response_message = json.dumps({"message": "Logcat already running", "session_id": session_id})
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(response_message.encode())
            print(f'Responded to {self.path} with {response_message}')
        
        elif self.path.startswith('/ios/start'):
            session_id, raw_log_path, structured_log_path = generate_session_id()
            active_sessions[session_id] = datetime.now()
            saved_sessions[session_id] = active_sessions[session_id]

            if ios_process is None:
                ios_output = io.StringIO()
                ios_process = subprocess.Popen(['python', 'ios.py', session_id], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                ios_thread = threading.Thread(target=self.capture_ios_output, args=(ios_process, ios_output, raw_log_path))
                ios_thread.start()
                response_message = json.dumps({"message": "iOS syslog capture started", "session_id": session_id})
            else:
                response_message = json.dumps({"message": "iOS syslog capture already running", "session_id": session_id})

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(response_message.encode())

        elif self.path.startswith('/android/stop'):
            session_id = self.path.split('/')[-1]
            if logcat_process is not None and session_id in active_sessions:
                logcat_process.terminate()
                logcat_process.wait()
                logcat_thread.join()
                logcat_process = None
                del active_sessions[session_id]

                from android import main as parse_logs
                parsed_logs = parse_logs(session_id, filter_for_display=True)

                response_message = json.dumps(parsed_logs)
            else:
                response_message = "No active logcat process or invalid session ID."
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(response_message.encode())

        elif self.path.startswith('/ios/stop'):
            session_id = self.path.split('/')[-1]
            if ios_process is not None and session_id in active_sessions:
                ios_process.terminate()
                ios_process.wait()
                ios_thread.join()
                ios_process = None
                del active_sessions[session_id]

                from ios import main as parse_logs
                parsed_logs = parse_logs(session_id, filter_for_display=True)

                response_message = json.dumps(parsed_logs)
            else:
                response_message = "No active iOS process or invalid session ID."
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(response_message.encode())
        
        elif self.path.startswith('/download'):
            session_id = self.path.split('/')[-1]
            structured_log_path = os.path.join(LOGS_STRUCTURED_DIR, f'logs_structured_{session_id}.csv')
            
            if os.path.exists(structured_log_path):
                self.send_response(200)
                self.send_header('Content-Disposition', f'attachment; filename="logs_structured_{session_id}.csv"')
                self.send_header('Content-type', 'text/csv')
                self.end_headers()
                with open(structured_log_path, 'rb') as file:
                    shutil.copyfileobj(file, self.wfile)
                print(f"Sent download for session {session_id}")
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Log file not found.")

        else:
            self.send_response(404)
            self.end_headers()

    def capture_logcat_output(self, process, output_buffer, raw_log_path):
        try:
            for line in process.stdout:
                decoded_line = line.decode('utf-8', errors='replace')
                output_buffer.write(decoded_line)
            
            os.makedirs(os.path.dirname(raw_log_path), exist_ok=True)
            with open(raw_log_path, 'w', encoding='utf-8', errors='replace') as f:
                f.write(output_buffer.getvalue())
        
        except Exception as e:
            print(f"Error capturing logcat output: {e}")

    def capture_ios_output(self, process, output_buffer, raw_log_path):
        try:
            for line in process.stdout:
                decoded_line = line.decode('utf-8', errors='replace')
                output_buffer.write(decoded_line)
            
            os.makedirs(os.path.dirname(raw_log_path), exist_ok=True)
            with open(raw_log_path, 'w', encoding='utf-8', errors='replace') as f:
                f.write(output_buffer.getvalue())
        
        except Exception as e:
            print(f"Error capturing iOS syslog output: {e}")

def schedule_log_cleanup():
    expiration_time = timedelta(hours=1)
    now = datetime.now()
    for session_id, start_time in list(saved_sessions.items()):
        if now - start_time > expiration_time:
            raw_log_path = os.path.join(LOGS_RAW_DIR, f'logs_{session_id}.txt')
            structured_log_path = os.path.join(LOGS_STRUCTURED_DIR, f'logs_structured_{session_id}.csv')
            print(f"Attempting to delete {raw_log_path} and {structured_log_path}")
            if os.path.exists(raw_log_path):
                os.remove(raw_log_path)
                print(f"Deleted {raw_log_path}")
            else:
                print(f"{raw_log_path} does not exist")
            if os.path.exists(structured_log_path):
                os.remove(structured_log_path)
                print(f"Deleted {structured_log_path}")
            else:
                print(f"{structured_log_path} does not exist")
            del saved_sessions[session_id]
        else:
            print(f"Session {session_id} has not expired yet")

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    schedule.every(5).minutes.do(schedule_log_cleanup)
    threading.Thread(target=run_scheduler).start()
    run()