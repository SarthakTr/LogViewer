# Log Analyser

## Project Description
This project is a comprehensive log analysis application designed for Android. The app displays system and application logs and analyzes them in real time to detect potential security issues and operational problems. By monitoring log data, the app can help identify vulnerabilities, anomalous behavior, and other issues that could compromise the security or stability of the system. With a user-friendly interface and automated analysis capabilities, this tool is essential for anyone looking to enhance the security and reliability of their Android device.

## Requirements
To set up this project, you will need the following:
- Android Studio (version 2023.3.1 or higher)
- Java Development Kit (JDK) version 17.0.12
- Gradle (version 8.6)
- Android SDK version 13.0
- External storage access permissions for saving log files (for Android versions below 13)

## Installation

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/SarthakTr/LogViewer
    cd LogViewer
    ```

2. **Open in Android Studio:**
    - Open Android Studio.
    - Click on "Open an existing project."
    - Navigate to the cloned repository and select it.

3. **Sync Project with Gradle:**
    - Allow Android Studio to sync with Gradle files.
    - Ensure that all dependencies are installed correctly.

4. **Set Up Permissions:**
    - For Android 13 and above, ensure that the app requests `READ_MEDIA_IMAGES`, `READ_MEDIA_VIDEO`, and `READ_MEDIA_AUDIO` permissions if you need media access.
    - For older versions, ensure proper handling of `READ_EXTERNAL_STORAGE` and `WRITE_EXTERNAL_STORAGE` permissions.

## Usage

1. **Run the App:**
    - Click the "Run" button in Android Studio or use an emulator to start the app on a connected device.

2. **Start Logging:**
    - Press the "Start" button to initiate logging. The app will capture logs using `adb logcat`.

3. **Stop Logging:**
    - Press the "Stop" button to stop the logging process. The logs will be displayed on the screen.

4. **Save Logs:**
    - Press the "Save" button to save the captured logs as a text file on your device.

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -m 'Add some YourFeature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a pull request.

## License
This project is licensed under the MIT License.
