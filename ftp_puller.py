import os
import csv
import re
from ftplib import FTP

# Configuration
CSV_FOLDER = r"G:\My Drive\claude code work\wafer_ftp_puller\datatable"
DOWNLOAD_DIR = r"G:\My Drive\FTP data"

FTP_HOST = "ftp.chipbond.com.tw"
FTP_USER = "avago"
FTP_PASS = "5rtfgvb$"
BASE_FTP_PATH = "/avago/FTP/EBR_data"

def sanitize_ftp_path(raw_path):
    """Clean Windows network paths or relative subpaths into clean FTP relative paths."""
    if not raw_path:
        return ""
    # Remove leading backslashes, drive letters, and normalize slashes
    clean_path = raw_path.replace("\\", "/").strip()
    clean_path = re.sub(r"^.*?/avago/FTP/EBR_data/", "", clean_path, flags=re.IGNORECASE)
    clean_path = clean_path.lstrip("/")
    return clean_path

def get_ftp_paths_from_csvs():
    """Reads all CSVs in the datatable folder and retrieves the Path column (index 9)."""
    targets = set()
    if not os.path.exists(CSV_FOLDER):
        print(f"Directory not found: {CSV_FOLDER}")
        return targets

    for file in os.listdir(CSV_FOLDER):
        if file.endswith(".csv"):
            filepath = os.path.join(CSV_FOLDER, file)
            try:
                with open(filepath, mode="r", encoding="utf-8-sig") as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                    if len(rows) >= 2 and len(rows[1]) >= 10:
                        raw_path = rows[1][9].strip() # Column 10 (Path)
                        clean = sanitize_ftp_path(raw_path)
                        if clean:
                            targets.add(clean)
            except Exception as e:
                print(f"Error reading {file}: {e}")
    return targets

def download_from_ftp(targets):
    """Connects to Chipbond FTP and downloads the target files/directories."""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    print(f"Connecting to {FTP_HOST}...")
    ftp = FTP(FTP_HOST)
    ftp.login(user=FTP_USER, passwd=FTP_PASS)
    print("Logged in successfully.")

    for target in targets:
        full_ftp_path = f"{BASE_FTP_PATH}/{target}".replace("//", "/")
        print(f"\nProcessing target: {full_ftp_path}")

        try:
            # Determine if target is a file or folder
            parent_dir = os.path.dirname(full_ftp_path)
            target_name = os.path.basename(full_ftp_path)

            ftp.cwd(parent_dir)
            files_in_dir = ftp.nlst()

            if target_name in files_in_dir:
                # Target is a specific file
                local_file_path = os.path.join(DOWNLOAD_DIR, target_name)
                if not os.path.exists(local_file_path):
                    print(f"Downloading file: {target_name}...")
                    with open(local_file_path, "wb") as f:
                        ftp.retrbinary(f"RETR {target_name}", f.write)
                    print(f"Saved to {local_file_path}")
                else:
                    print(f"File already exists locally: {target_name}")
            else:
                # Attempt directory traversal if target is a folder
                ftp.cwd(full_ftp_path)
                folder_files = ftp.nlst()
                for f_name in folder_files:
                    local_file_path = os.path.join(DOWNLOAD_DIR, f_name)
                    if not os.path.exists(local_file_path):
                        print(f"Downloading: {f_name}...")
                        with open(local_file_path, "wb") as f:
                            ftp.retrbinary(f"RETR {f_name}", f.write)
                        print(f"Saved to {local_file_path}")
                    else:
                        print(f"File already exists: {f_name}")

        except Exception as e:
            print(f"Failed to process {target}: {e}")

    ftp.quit()
    print("\nFTP Download Task Finished.")

if __name__ == "__main__":
    target_paths = get_ftp_paths_from_csvs()
    print(f"Found {len(target_paths)} unique FTP targets to pull.")
    if target_paths:
        download_from_ftp(target_paths)