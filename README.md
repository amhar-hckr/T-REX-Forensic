# 🛰️ T-REX Forensic Tool

**T-REX Forensic Tool** is a cross-platform forensic analysis tool designed for file and folder analysis. It provides a sleek, sci-fi-inspired interface with advanced forensic capabilities, making it a powerful tool for investigators and enthusiasts alike.

---

## 🚀 Features

- **Text Extraction**: Extract readable strings from files using `strings`.
- **Metadata Analysis**: Analyze file metadata using `exiftool`.
- **Hex Dump**: Generate a hex dump of files using `xxd`.
- **File Content Viewer**: View file contents using `cat` (Linux) or `type` (Windows).
- **Base64 Encoding**: Encode files to Base64 format.
- **Backup Creation**: Create backup copies of files.
- **Remote Forensics**: Connect to a remote system for forensic operations.
- **File Carving**: Recover deleted files using `foremost`.
- **File Hashing**: Generate and verify file hashes using `hashdeep`.
- **Memory Forensics**: Analyze memory dumps using `volatility`.
- **Firmware Analysis**: Analyze firmware files using `binwalk`.
- **Network Traffic Capture**: Capture network traffic using `tcpdump`.
- **Malware Detection**: Scan files for malware using `yara`.
- **File Encryption**: Encrypt files using `gpg`.
- **Rootkit Detection**: Detect rootkits using `chkrootkit` and `rkhunter`.
- **Network Traffic Analysis**: Analyze network traffic using `tshark`.
- **Incident Response**: Perform live system triage using `dfirtriage`.
- **Antivirus Scanning**: Scan files for malware using `clamav`.
- **Digital Forensics Platform**: Launch `autopsy` for advanced forensic analysis.
- **Steganography Detection**: Detect and extract hidden data using `openstego`.
- **Data Extraction**: Extract useful information from disk images using `bulk_extractor`.

---

## 🛠️ Tools and Their Purposes

| Tool/Feature         | Purpose                                                                 |
|-----------------------|------------------------------------------------------------------------|
| `strings`            | Extract readable text from binary files.                                |
| `exiftool`           | Extract metadata from files like images, documents, and videos.         |
| `xxd`                | Generate a hexadecimal representation of a file's contents.             |
| `cat`/`type`         | View file contents in the terminal.                                     |
| `base64`/`certutil`  | Encode files into Base64 format for secure transmission or storage.     |
| Backup Creation      | Create a backup copy of the selected file.                              |
| Remote Forensics     | Connect to a remote system for forensic operations.                     |
| `foremost`           | Recover deleted files from disk images or raw data.                     |
| `hashdeep`           | Generate and verify file hashes for integrity checks.                   |
| `volatility`         | Analyze memory dumps for forensic artifacts.                            |
| `binwalk`            | Extract and analyze embedded files in firmware images.                  |
| `tcpdump`            | Capture and analyze network traffic.                                    |
| `yara`               | Scan files for malware signatures using YARA rules.                     |
| `gpg`                | Encrypt and decrypt files for secure storage.                           |
| `chkrootkit`         | Detect rootkits on Linux systems.                                       |
| `rkhunter`           | Scan for rootkits, backdoors, and local exploits.                       |
| `tshark`             | Capture and analyze network traffic (CLI version of Wireshark).         |
| `dfirtriage`         | Collect forensic artifacts from a live system.                          |
| `clamav`             | Scan files for viruses and malware.                                     |
| `autopsy`            | GUI-based forensic analysis platform for advanced investigations.       |
| `openstego`          | Detect and extract hidden data in files (steganography).                |
| `bulk_extractor`     | Extract useful information (e.g., emails, credit card numbers) from disk images. |

---

## 🕹️ Usage

1. Run the tool:
   ```bash
   python3 T-REXForansic.py

2. Install Python dependencies:
    ```bash
    python3 -m pip install -r Requirements.txt

Ensure required tools are installed (see the Requirements section).

🕹️ Usage
3. Run the tool:
    ```bash
    python3 T-REXForansic.py`

Follow the on-screen prompts to:

Select a file or folder for analysis.
Choose a forensic operation from the menu.

Example Workflow
Select a file or folder path.
Choose an operation (e.g., 1 for strings).
View the output or results in the terminal.

 
🛡️ Menu Options
Option	Description
1	Extract readable strings from files
2	Analyze file metadata
3	Generate a hex dump of files
4	View file contents
5	Encode files to Base64
6	Create a backup copy of files
7	Connect to a remote system
8	Exit the tool
9	Recover deleted files with foremost
10	Generate file hashes with hashdeep
11	Analyze memory dumps with volatility
12	Analyze firmware files with binwalk
13	Capture network traffic with tcpdump
14	Scan files for malware with yara
15	Encrypt files with gpg
16	Detect rootkits with chkrootkit
17	Detect rootkits with rkhunter
18	Analyze network traffic with tshark
19	Perform live system triage with dfirtriage
20	Scan files for malware with clamav
21	Launch autopsy for advanced forensic analysis
22	Detect and extract hidden data with openstego
23	Extract data from disk images with bulk_extractor

📂 Logging
Logs are saved in the logs directory with a timestamped filename.
Backup files are stored in the ForensicSpy_Backup directory under the user's home folder.

🛠️ Troubleshooting
Missing Tools: If a required tool is not found, the tool will prompt you to install it automatically.
Permission Issues: Run the script with admin/root privileges if required:
Linux: sudo python3 T-REXForansic.py
Windows: Run the terminal as Administrator.
🌌 Sci-Fi Experience
Enjoy a futuristic terminal interface with:

Animated Scanning Effects
Rich Progress Bars
Stylized ASCII Art Banners
🤝 Contributing
Contributions are welcome! Feel free to submit issues or pull requests to improve the tool.

📜 License
This project is licensed under the MIT License. See the LICENSE file for details.

👨‍💻 Author
Developed by Amhar.

🌟 Star Us on GitHub!
If you find this tool useful, please give it a ⭐ on GitHub!
