import os
import paramiko
from scp import SCPClient

def choose_remote_file(ssh, remote_dir):
    """List files on remote and let user choose one."""
    
    stdin, stdout, stderr = ssh.exec_command(f"ls -1 {remote_dir}")
    files = stdout.read().decode().splitlines()

    if not files:
        print("No files found in remote directory.")
        return None

    print("\nAvailable remote files:")
    for i, f in enumerate(files, 1):
        print(f"{i}. {f}")

    choice = input("\nEnter number of file to copy: ")
    try:
        index = int(choice) - 1
        if 0 <= index < len(files):
            return remote_dir + '/' + files[index]
    except ValueError:
        pass

    print("Invalid choice.")
    return None


def copy_file_from_remote(remote_host, remote_user, remote_dir, local_dir, password=None):
    """Copy a chosen file from remote host to local directory via SCP."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(remote_host, username=remote_user, password=password)

    remote_file = choose_remote_file(ssh, remote_dir)
    if not remote_file:
        ssh.close()
        return

    os.makedirs(local_dir, exist_ok=True)
    local_path = os.path.join(local_dir, os.path.basename(remote_file))

    with SCPClient(ssh.get_transport()) as scp:
        print(f"Downloading {remote_file} -> {local_path}")
        scp.get(remote_file, local_path)
        print(f"✅ File copied to {local_path}")

    ssh.close()


if __name__ == "__main__":
    remote_host = input("Enter remote host (IP or hostname): ").strip()
    remote_user = input("Enter SSH username: ").strip()
    remote_dir = input("Enter remote directory path: ").strip()

    
    local_dir = input("Enter local directory to save file: ").strip()
    password = input("Enter SSH password (leave blank for key auth): ").strip() or None

    copy_file_from_remote(remote_host, remote_user, remote_dir, local_dir, password)
