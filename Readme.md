# T-REX Forensic Tool

T-REX Forensic Tool is a cross-platform forensic analysis tool designed to assist in analyzing files and folders using various utilities such as `strings`, `exiftool`, `xxd`, and more. It supports both Linux and Windows environments and provides a user-friendly CLI interface with rich visuals.

---

## Features

- **Text Extraction**: Extract readable strings from files using `strings`.
- **Metadata Analysis**: Analyze file metadata using `exiftool`.
- **Hex Dump**: Generate a hex dump of files using `xxd`.
- **File Content Viewer**: View file contents using `cat` (Linux) or `type` (Windows).
- **Base64 Encoding**: Encode files to Base64 format.
- **Backup Creation**: Create backup copies of files.
- **Remote Forensics**: Connect to a remote system for forensic operations.
- **Cross-Platform**: Works on both Linux and Windows systems.

---

## Requirements

### Linux
- Python 3.6 or higher
- Tools:
  - `strings` (Install via `sudo apt-get install binutils`)
  - `exiftool` (Install via `sudo apt-get install libimage-exiftool-perl`)
  - `xxd` (Install via `sudo apt-get install xxd`)

### Windows
- Python 3.6 or higher
- Tools:
  - `strings.exe` (Install via Chocolatey: `choco install strings`)
  - `exiftool.exe` (Install via Chocolatey: `choco install exiftool`)
  - `xxd.exe` (Install via Chocolatey: `choco install vim`)

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/T-REXForensic.git
   cd T-REXForensic