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
from pyfiglet import figlet_format
from datetime import datetime
from rich.live import Live
from rich.panel import Panel
from rich.align import Align
from rich.theme import Theme
import getpass
import platform

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

# Platform-specific tool information
TOOLS_INFO = {
    "Linux": {
        "strings": {"install": "sudo apt-get install binutils", "command": "strings"},
        "exiftool": {"install": "sudo apt-get install libimage-exiftool-perl", "command": "exiftool"},
        "xxd": {"install": "sudo apt-get install xxd", "command": "xxd"},
        "base64": {"command": "base64"}
    },
    "Windows": {
        "strings": {"install": "choco install strings", "command": "strings.exe"},
        "exiftool": {"install": "choco install exiftool", "command": "exiftool.exe"},
        "xxd": {"install": "choco install vim", "command": "xxd.exe"},
        "base64": {"command": "certutil"}
    }
}

def get_tools_info():
    system = platform.system()
    return TOOLS_INFO.get(system, TOOLS_INFO["Linux"])  # Default to Linux if unknown system

def banner():
    console.print(figlet_format("ForensicSpy", font="slant"), style="bold green")
    console.print(f"[bold cyan]Author:[/] Launch • [bold yellow]{platform.system()} Edition\n")

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

def get_file_or_folder():
    while True:
        path = console.input("\n[bold white]Enter the path to a file or folder:[/] ").strip()
        if os.path.exists(path):
            return path
        console.print("[red][✗] Path does not exist. Please try again.[/]")

def show_menu():
    console.rule("[bold green] Forensic Operations ")
    table = Table(title="Available Tools", style="bold magenta")
    table.add_column("Option", style="cyan")
    table.add_column("Description", style="yellow")
    
    menu_options = [
        ("1", "strings (text extraction)"),
        ("2", "exiftool (metadata)"),
        ("3", "xxd (hex dump)"),
        ("4", "cat/type (view contents)"),
        ("5", "base64/certutil (encode file)"),
        ("6", "Create backup copy"),
        ("7", "Remote Forensics"),
        ("8", "Exit")
    ]
    
    for opt in menu_options:
        table.add_row(*opt)
    
    console.print(table)

def run_command(choice, filepath):
    tools_info = get_tools_info()
    
    try:
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
            path = get_file_or_folder()
            show_menu()
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