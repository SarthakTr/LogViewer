# LogViewer — Mobile Event Log Extractor

**LogViewer** is a cross-platform tool that enables mobile developers, testers, and analysts to extract, analyze, and download event logs from Android and iOS devices in a structured format. It consists of three key components:

- A **Flutter-based mobile frontend**
- A **Flask communication layer**
- A **Python backend server**

## 📦 Repository Structure

```
logviewer/
├── frontend/         # Flask layer for mobile-backend communication
├── backend/          # Core Python backend for log extraction and parsing
```

## ✅ Features

- Extract logs from Android via ADB
- Capture syslogs from iOS using `libimobiledevice`
- Parse logs and store them in structured CSV format
- Download logs from mobile device (via app or browser)
- Lightweight architecture with no cloud dependencies

## 📂 Output

All logs are saved as CSV files with structured fields such as:
- Timestamp (date/time/millisecond)
- Log level (F/E/W/D/I/V)
- Component
- Message content

Files are stored in the Downloads directory on the device or returned directly via HTTP.

## 📋 Requirements

- Python 3.7+
- Flask
- ADB (for Android)
- `libimobiledevice` (for iOS)
- Flutter (optional, for app interface)

## 🤝 Contributing

We welcome improvements! Submit a pull request or open an issue.