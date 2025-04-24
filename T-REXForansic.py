#!/usr/bin/env python3
import os
import subprocess
import shutil
import urllib.request
import zipfile
import sys
import time
import socket
import sqlite3
import logging
import argparse
from time import sleep
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.align import Align
from rich.theme import Theme
from rich.layout import Layout
from pyfiglet import figlet_format
from datetime import datetime
import getpass
import platform
import ctypes
import threading

theme = Theme({
    "info": "bold cyan",
    "warning": "bold yellow",
    "error": "bold red",
    "success": "bold green",
    "header": "bold magenta",
    "footer": "dim cyan",
    "panel_border": "bright_cyan"
})
console = Console(theme=theme)

#==================
# CTRL + C HANDLER
#==================
def update_logs(self):
    if self.log_lines:
        line = self.log_lines.pop(0)
        self.text_box.append(line)
    else:
        self.timer.stop()
        self.close()

        # CLEAR TERMINAL before main()
        os.system('cls' if os.name == 'nt' else 'clear')

        # THEN start main()
        threading.Timer(0.2, main).start()

# 🧪 Live Dashboard and Terminal Visuals
def live_dashboard():
    console = Console()
    with Live(Panel("🛰️ Scanning filesystem...", border_style="blue"), refresh_per_second=4):
        time.sleep(5)  # simulate scanning

def send_file(conn, file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
        conn.sendall(data)
       
def scanning_effect(text="Analyzing file..."):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(0.03)

console = Console(theme=Theme({
    "info": "dim cyan",
    "success": "bold green",
    "error": "bold red",
}))

def parse_args():
    parser = argparse.ArgumentParser(description="ForensicSpy CLI Tool")
    parser.add_argument('--check-tools', action='store_true', help="Check for required forensic tools.")
    parser.add_argument('--update-tools', action='store_true', help="Update/download missing forensic tools.")
    return parser.parse_args()

LOG_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logger(username, filepath=None):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if filepath:
        backup_dir = os.path.join(os.path.expanduser("~"), "ForensicSpy_Backup")
        os.makedirs(backup_dir, exist_ok=True)
        backup_path = os.path.join(backup_dir, f"{os.path.basename(filepath)}_{timestamp}.backup")
    else:
        backup_path = None

    log_filename = f"{username}_{timestamp}.log"
    log_path = os.path.join(LOG_DIR, log_filename)
    
    return log_path, backup_path

TOOLS_DIR = os.path.join(os.getcwd(), "tools")

# ======================
# DEPENDENCY MANAGEMENT
# ======================
TOOLS_INFO = {
    "Linux": {
        "strings": {"install": "sudo apt-get install binutils", "command": "strings"},
        "exiftool": {"install": "sudo apt-get install libimage-exiftool-perl", "command": "exiftool"},
        "xxd": {"install": "sudo apt-get install xxd", "command": "xxd"},
        "foremost": {"install": "sudo apt-get install foremost", "command": "foremost"},
        "hashdeep": {"install": "sudo apt-get install hashdeep", "command": "hashdeep"},
        "volatility": {"install": "sudo apt-get install volatility", "command": "volatility"},
        "binwalk": {"install": "sudo apt-get install binwalk", "command": "binwalk"},
        "tcpdump": {"install": "sudo apt-get install tcpdump", "command": "tcpdump"},
        "yara": {"install": "sudo apt-get install yara", "command": "yara"},
        "gpg": {"install": "sudo apt-get install gnupg", "command": "gpg"},
        "chkrootkit": {"install": "sudo apt-get install chkrootkit", "command": "chkrootkit"},
        "rkhunter": {"install": "sudo apt-get install rkhunter", "command": "rkhunter"},
        "tshark": {"install": "sudo apt-get install tshark", "command": "tshark"},
        "clamav": {"install": "sudo apt-get install clamav", "command": "clamscan"},
        "autopsy": {"install": "sudo apt-get install autopsy", "command": "autopsy"},
        "openstego": {"install": "sudo apt-get install openstego", "command": "openstego"},
        "bulk_extractor": {"install": "sudo apt-get install bulk-extractor", "command": "bulk_extractor"}
    },
    "Windows": {
        "strings": {"install": "choco install strings", "command": "strings.exe"},
        "exiftool": {"install": "choco install exiftool", "command": "exiftool.exe"},
        "xxd": {"install": "choco install vim", "command": "xxd.exe"},
        "foremost": {"install": "choco install foremost", "command": "foremost.exe"},
        "hashdeep": {"install": "choco install hashdeep", "command": "hashdeep.exe"},
        "volatility": {"install": "choco install volatility", "command": "volatility.exe"},
        "binwalk": {"install": "choco install binwalk", "command": "binwalk.exe"},
        "tcpdump": {"install": "choco install tcpdump", "command": "tcpdump.exe"},
        "yara": {"install": "choco install yara", "command": "yara.exe"},
        "gpg": {"install": "choco install gpg4win", "command": "gpg.exe"},
        "chkrootkit": {"install": "manual installation required", "command": "chkrootkit.exe"},
        "rkhunter": {"install": "manual installation required", "command": "rkhunter.exe"},
        "tshark": {"install": "choco install wireshark", "command": "tshark.exe"},
        "clamav": {"install": "choco install clamav", "command": "clamscan.exe"},
        "autopsy": {"install": "manual installation required", "command": "autopsy.exe"},
        "openstego": {"install": "manual installation required", "command": "openstego.exe"},
        "bulk_extractor": {"install": "manual installation required", "command": "bulk_extractor.exe"}
    }
}

# ======================
# SYSTEM AND ENVIRONMENT CHECKS
# ======================
def get_tools_info():
    system = platform.system()
    return TOOLS_INFO.get(system, TOOLS_INFO["Linux"])  # Default to Linux if unknown system

# ======================
# BANNER 
# ======================
def banner():
    console.print(figlet_format("ForensicSpy", font="slant"), style="bold green")
    console.print(f"[bold cyan]Author:[/] AMHAR • [bold yellow]{platform.system()} Edition\n")


# ======================
# CHECK PRIVILLAGE 
# ======================
def is_admin():
    """Check if the script is running with admin privileges"""
    try:
        if platform.system() == "Windows":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except:
        return False

def run_as_admin():
    """Re-launch the script with admin privileges"""
    if not is_admin():
        console.print("[red]This script requires admin/root permissions to run.[/]")
        if platform.system() == "Windows":
            # Re-run with Windows UAC elevation
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        else:
            # Re-run with sudo on Linux
            os.execvp('sudo', ['sudo', 'python3'] + sys.argv)
        sys.exit()

def clear_terminal():
    """Clear the terminal screen."""
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def download_with_rich_progress(url, dest_path):
    try:
        with Progress(
            SpinnerColumn(style="cyan"),
            "[progress.description]{task.description}",
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            transient=True,
        ) as progress:
            task = progress.add_task("[yellow]Downloading...", total=None)
            urllib.request.urlretrieve(url, dest_path, 
                lambda block_num, block_size, total_size: progress.update(
                    task, total=total_size, 
                    completed=block_num * block_size
                ) if total_size > 0 else None
            )
            progress.update(task, completed=1)
            sleep(0.2)
    except Exception as e:
        console.print(f"[red]Download failed: {e}[/]")

def install_tool(tool_name, info):
    if "install" not in info:
        console.print(f"[yellow]No install command available for {tool_name}[/]")
        return False
        
    console.print(f"\n[bold yellow][+] Installing {tool_name}...[/]")
    try:
        if platform.system() == "Windows":
            subprocess.run(info["install"], shell=True, check=True)
        else:
            subprocess.run(info["install"].split(), check=True)
        console.print(f"[green][✓] Successfully installed {tool_name}[/]")
        return True
    except subprocess.CalledProcessError as e:
        console.print(f"[red][✗] Failed to install {tool_name}:[/] {e}")
        return False
    except Exception as e:
        console.print(f"[red][✗] Error installing {tool_name}:[/] {e}")
        return False
    
def provide_manual_install_instructions(tool_name):
    """Provide manual installation instructions for specific tools."""
    if tool_name == "volatility":
        console.print("[yellow][!] Volatility is not available in the default repositories.[/]")
        console.print("[cyan]Please download and install it manually from the official GitHub repository:[/]")
        console.print("[blue]https://github.com/volatilityfoundation/volatility[/]")
    elif tool_name == "openstego":
        console.print("[yellow][!] OpenStego is not available in the default repositories.[/]")
        console.print("[cyan]Please download and install it manually from the official GitHub repository:[/]")
        console.print("[blue]https://github.com/syvaidya/openstego[/]")
    else:
        console.print(f"[yellow][!] {tool_name} is not available for automatic installation. Please refer to its official documentation for installation instructions.[/]")    


def check_dependencies():
    console.rule("[bold red] Dependency Check ")
    tools_info = get_tools_info()
    
    for tool_name, info in tools_info.items():
        if shutil.which(info["command"]):
            console.print(f"[green][✓] {tool_name} found.[/]")
        else:
            console.print(f"[yellow][!] {tool_name} not found.[/]")
            if "install" in info:
                choice = console.input("    [bold white]May I install it for you? Y or N (Default Y):[/] ").strip().lower()
                if choice in ["", "y"]:
                    install_tool(tool_name, info)
                else:
                    console.print(f"[red][⚠] Please manually install {tool_name}[/]")
            else:
                console.print(f"[red][⚠] {tool_name} is required but cannot be auto-installed[/]")

def connect_to_remote():
    host = console.input("[bold white]Enter the remote host IP: [/]").strip()
    port = 9999
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)
            s.connect((host, port))
            console.print(f"[green]Connected to remote system at {host}:{port}[/]")
            
            command = "status"
            s.sendall(command.encode())
            
            data = s.recv(1024)
            console.print(f"[cyan]Received: {data.decode()}[/]")
            return True
    except Exception as e:
        console.print(f"[red]Connection failed: {e}[/]")
        return False

def get_username():
    """Cross-platform username retrieval"""
    try:
        return getpass.getuser()
    except Exception:
        try:
            if platform.system() == "Windows":
                return os.environ.get('USERNAME', 'unknown')
            else:
                return os.environ.get('USER', 'unknown')
        except Exception:
            return 'unknown'

# ======================
# FILE AND FOLDER OPERATIONS     
# Folder Verification
# ====================
def get_file_or_folder():
    while True:
        path = console.input("\n[bold white]Enter the path to a file or folder:[/] ").strip()
        if os.path.exists(path):
            return path
        console.print("[red][✗] Path does not exist. Please try again.[/]")

# ======================
# USER INTERACTION OPTIONS
# ======================
def show_menu():
    print("Updating body with menu...")  # Debugging statement
    table = Table(title="Available Tools", show_header=True, header_style="bold magenta")
    table.add_column("Option", style="cyan", width=12)
    table.add_column("Description", style="yellow")
    
    menu_options = [
        ("1", "strings (text extraction)"),
        ("2", "exiftool (metadata)"),
        ("3", "xxd (hex dump)"),
        ("4", "cat/type (view contents)"),
        ("5", "base64/certutil (encode file)"),
        ("6", "Create backup copy"),
        ("7", "Remote Forensics"),
        ("8", "Exit"),
        ("9", "foremost (file carving)"),
        ("10", "hashdeep (file hashing)"),
        ("11", "volatility (memory analysis)"),
        ("12", "binwalk (firmware analysis)"),
        ("13", "tcpdump (network traffic capture)"),
        ("14", "yara (malware detection)"),
        ("15", "gpg (file encryption)"),
        ("16", "chkrootkit (rootkit detection)"),
        ("17", "rkhunter (rootkit detection)"),
        ("18", "tshark (network traffic analysis)"),
        ("19", "dfirtriage (incident response)"),
        ("20", "clamav (antivirus scanning)"),
        ("21", "autopsy (digital forensics platform)"),
        ("22", "openstego (steganography detection)"),
        ("23", "bulk_extractor (data extraction)")
    ]  
    
    for opt in menu_options:
        table.add_row(*opt)
  
    console.print(table)


# ======================
# COMMAND EXECUTION
# ======================
def run_command(choice, filepath):
    tools_info = get_tools_info()
    
    try:
         # Clear the terminal and re-display the banner and author logos
        clear_terminal()
        banner()

        if os.path.isdir(filepath):
            files = [f for f in os.listdir(filepath) if os.path.isfile(os.path.join(filepath, f))]
            if not files:
                console.print("[red]No files found in directory[/]")
                return True
                
            console.print("\n[bold cyan]Available Files:[/]")
            for i, f in enumerate(files):
                console.print(f"[{i}] {f}")
                
            try:
                selected = int(console.input("\nSelect file: ").strip())
                filepath = os.path.join(filepath, files[selected])
            except (ValueError, IndexError):
                console.print("[red]Invalid selection[/]")
                return True

        console.print(f"[green]Selected: {filepath}[/]")

        if choice == '1':  # strings
            cmd = [tools_info["strings"]["command"], filepath]
        
        elif choice == '2':  # exiftool
            cmd = [tools_info["exiftool"]["command"], filepath]
            
        elif choice == '3':  # xxd
            cmd = [tools_info["xxd"]["command"], filepath]
            
        elif choice == '4':  # view contents
            cmd = ["type", filepath] if platform.system() == "Windows" else ["cat", filepath]
            
        elif choice == '5':  # base64 encode
            encoded_file = filepath + ".b64"
            if platform.system() == "Windows":
                cmd = ["certutil", "-encode", filepath, encoded_file]
            else:
                cmd = ["base64", "-i", filepath, "-o", encoded_file]
                
        elif choice == '6':  # backup
            backup_path = filepath + ".backup"
            shutil.copy2(filepath, backup_path)
            console.print(f"[green]Backup created: {backup_path}[/]")
            return True
            
        elif choice == '7':  # remote
            return connect_to_remote()
            
        elif choice == '8':  # exit
            return False
        
        elif choice == '9':  # File carving with foremost
            output_dir = os.path.join(os.getcwd(), "foremost_output")
            os.makedirs(output_dir, exist_ok=True)
            cmd = ["foremost", "-i", filepath, "-o", output_dir]
            console.print(f"[cyan]Recovering files to: {output_dir}[/]")

        elif choice == '10':  # File hashing with hashdeep
            cmd = ["hashdeep", "-r", filepath]
            console.print(f"[cyan]Generating file hashes for: {filepath}[/]")

        elif choice == '11':  # Memory analysis with volatility
            cmd = ["volatility", "-f", filepath, "pslist"]
            console.print(f"[cyan]Analyzing memory dump: {filepath}[/]")

        elif choice == '12':  # Firmware analysis with binwalk
            cmd = ["binwalk", filepath]
            console.print(f"[cyan]Analyzing firmware file: {filepath}[/]")

        elif choice == '13':  # Network traffic capture with tcpdump
            output_file = os.path.join(os.getcwd(), "network_traffic.pcap")
            cmd = ["tcpdump", "-i", "eth0", "-w", output_file]
            console.print(f"[cyan]Capturing network traffic to: {output_file}[/]")

        elif choice == '14':  # Malware scanning with YARA
            rule_file = console.input("[bold]Enter YARA rule file path: [/]").strip()
            cmd = ["yara", rule_file, filepath]
            console.print(f"[cyan]Scanning file: {filepath} with YARA rules[/]")

        elif choice == '15':  # File encryption with GPG
            cmd = ["gpg", "-c", filepath]
            console.print(f"[cyan]Encrypting file: {filepath}[/]")

        elif choice == '16':  # Rootkit detection with chkrootkit
            cmd = ["chkrootkit"]
            console.print(f"[cyan]Scanning the system for rootkits...[/]")

        elif choice == '17':  # Rootkit detection with rkhunter
            cmd = ["rkhunter", "--check"]
            console.print(f"[cyan]Scanning the system for rootkits with rkhunter...[/]")

        elif choice == '18':  # Network traffic analysis with tshark
            output_file = os.path.join(os.getcwd(), "tshark_traffic.pcap")
            cmd = ["tshark", "-i", "eth0", "-w", output_file]
            console.print(f"[cyan]Capturing network traffic to: {output_file}[/]")

        elif choice == '19':  # Incident response triage with dfirtriage
            cmd = ["dfirtriage"]
            console.print(f"[cyan]Performing live system triage...[/]")

        elif choice == '20':  # Malware scanning with ClamAV
            cmd = ["clamscan", filepath]
            console.print(f"[cyan]Scanning file: {filepath} for malware...[/]")

        elif choice == '21':  # Launch Autopsy
            cmd = ["autopsy"]
            console.print(f"[cyan]Launching Autopsy for advanced forensic analysis...[/]")

        elif choice == '22':  # Steganography detection with OpenStego
            cmd = ["openstego", "extract", "-sf", filepath]
            console.print(f"[cyan]Extracting hidden data from: {filepath}[/]")

        elif choice == '23':  # Data extraction with bulk_extractor
            output_dir = os.path.join(os.getcwd(), "bulk_extractor_output")
            os.makedirs(output_dir, exist_ok=True)
            cmd = ["bulk_extractor", "-o", output_dir, filepath]
            console.print(f"[cyan]Extracting data to: {output_dir}[/]")
            
        else:
            console.print("[red]Invalid choice[/]")
            return True

        # Execute the command
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.stdout:
                console.print(f"\n[bold]Output:[/]\n{result.stdout}")
            if result.stderr:
                console.print(f"\n[red]Errors:[/]\n{result.stderr}")
        except subprocess.TimeoutExpired:
            console.print("[red]Command timed out[/]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
        logging.exception("Command failed")
        
    return True


# ======================
# MAIN APPLICATION
# ======================
def main():
    banner()
    check_dependencies()
    username = get_username()
    log_path, _ = setup_logger(username)
    
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    console.print(f"[blue]Log file: {log_path}[/]")
    
    try:
        while True:
            show_menu()
            path = get_file_or_folder()
            console.print(Panel(f"[bold green]📂 Selected Path:[/] {path}", title="Selected Path", border_style="cyan"))
            choice = console.input("[bold]Select option: [/]").strip()
            if not run_command(choice, path):
                break
    except KeyboardInterrupt:
        console.print("\n[red]Script terminated by user[/]")
    except Exception as e:
        console.print(f"[red]Fatal error: {e}[/]")
        logging.exception("Script crashed")
    finally:
        console.print("[green]ForensicSpy completed[/]")

if __name__ == "__main__":
    main()
