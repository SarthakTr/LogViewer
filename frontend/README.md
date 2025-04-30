# LogViewer — Flask Interface (Frontend)

This directory contains the Flask-based **frontend communication layer** for **LogViewer — Mobile Event Log Extractor**. It is designed to forward log-related requests from the mobile frontend (Flutter) to the core backend server responsible for log collection and processing.

> ⚠️ This is **not** the backend and does not perform log parsing or device communication. Refer to the `backend/` directory for that logic.

## ✅ Responsibilities

- Forwards API requests to the backend over HTTP
- Acts as a lightweight local communication layer between mobile frontend and backend
- Supports commands for:
  - Starting/stopping Android logcat
  - Starting/stopping iOS syslog
  - Downloading parsed logs from the backend

## 🧰 Requirements

- Python 3.7 or higher
- Flask
- Running backend server (see `../backend/server.py`)

Install dependencies:

```bash
pip install flask
```

## 🚀 Getting Started

1. Navigate to this directory:
   ```bash
   cd logviewer/frontend
   ```

2. Start the Flask server:
   ```bash
   python app.py
   ```

3. Access it via:
   ```
   http://127.0.0.1:5000
   ```

## 🔁 Communication Flow

The Flask server forwards predefined routes to the backend server, expected to be running at `http://127.0.0.1:8000` by default. Update this URL in `app.py` if needed:

```python
BACKEND_URL = "http://127.0.0.1:8000"
```

Supported routes:
- `/start_log` → Backend starts Android logcat
- `/stop_log` → Backend stops Android logcat
- `/start_ios_log` → Backend starts iOS syslog
- `/stop_ios_log` → Backend stops iOS syslog
- `/download_log` → Download the parsed log CSV

## 🧾 Notes

- This module does not handle any UI or direct device operations.
- Logs are saved and structured by the backend; this Flask layer only triggers those actions.

## 🤝 Contributing

Contributions and suggestions are welcome. Please open an issue or PR.