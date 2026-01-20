import os
import paramiko
from scp import SCPClient

CONFIG_FILE = "copy_hosts.txt"

def load_hosts_config(path=CONFIG_FILE):
    """Load known hosts from TXT config: host,user,password,default_remote_dir"""
    hosts = []
    if not os.path.exists(path):
        return hosts
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",")
            if len(parts) >= 2:
                host = parts[0].strip()
                user = parts[1].strip()
                password = parts[2].strip() if len(parts) > 2 else None
                default_remote_dir = parts[3].strip() if len(parts) > 3 else ""
                hosts.append({
                    "host": host,
                    "user": user,
                    "password": password,
                    "default_remote_dir": default_remote_dir
                })
    return hosts

def choose_remote_file(ssh, remote_dir):
    """List files on remote and let user choose one."""
    stdin, stdout, stderr = ssh.exec_command(f"ls -1 {remote_dir}")
    files = stdout.read().decode().splitlines()

    if not files:
        print("No files found in remote directory.")
        return None

    while True:
        print("\nAvailable remote files:")
        for i, f in enumerate(files, 1):
            print(f"{i}. {f}")

        choice = input("\nEnter number of file to copy: ").strip()
        try:
            index = int(choice) - 1
            if 0 <= index < len(files):
                return remote_dir + '/' + files[index]
        except ValueError:
            print("Invalid input, please enter a number.")
            continue

def copy_file_from_remote(host_info, remote_dir, local_dir):
    """Copy a chosen file from remote host to local directory via SCP."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host_info["host"], username=host_info["user"], password=host_info.get("password"))

    while True:
        remote_file = choose_remote_file(ssh, remote_dir)
        if not remote_file:
            print("No file selected. Exiting.")
            break

        os.makedirs(local_dir, exist_ok=True)
        local_path = os.path.join(local_dir, os.path.basename(remote_file))

        with SCPClient(ssh.get_transport()) as scp:
            print(f"Downloading {remote_file} -> {local_path}")
            scp.get(remote_file, local_path)
            print(f"File copied to {local_path}")

        again = input("Copy another file from this host? [y/N]: ").strip().lower()
        if again not in ("y", "yes"):
            break

    ssh.close()

if __name__ == "__main__":
    hosts = load_hosts_config()
    print("Known hosts:")
    for i, h in enumerate(hosts, 1):
        print(f"{i}. {h['host']} ({h['user']})")
    print(f"{len(hosts)+1}. Enter a custom host")

    choice = input(f"Choose a host [1-{len(hosts)+1}]: ").strip()
    try:
        index = int(choice) - 1
    except ValueError:
        index = len(hosts)  # default to custom host

    if 0 <= index < len(hosts):
        # Known host selected
        host_info = hosts[index]
        print(f"Selected {host_info['host']} ({host_info['user']})")
        remote_dir = host_info.get("default_remote_dir") or input("Enter remote directory to choose file from: ").strip()
        local_dir = input("Enter local directory to save file: ").strip()
        copy_file_from_remote(host_info, remote_dir, local_dir)
    else:
        # Custom host
        host = input("Enter remote host (IP or hostname): ").strip()
        user = input("Enter SSH username: ").strip()
        password = input("Enter SSH password (leave blank for key auth): ").strip() or None
        remote_dir = input("Enter remote directory path: ").strip()
        local_dir = input("Enter local directory to save file: ").strip()
        host_info = {"host": host, "user": user, "password": password}
        copy_file_from_remote(host_info, remote_dir, local_dir)
