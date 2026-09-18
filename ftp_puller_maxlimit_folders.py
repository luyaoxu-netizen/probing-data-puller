import os
import csv
import re
from ftplib import FTP

# Configuration
CSV_FOLDER = r"G:\My Drive\claude code work\wafer_ftp_puller\datatable"
BASE_DOWNLOAD_DIR = r"G:\My Drive\FTP data"

FTP_HOST = "ftp.chipbond.com.tw"
FTP_USER = "avago"
FTP_PASS = "5rtfgvb$"
BASE_FTP_PATH = "/avago/FTP/EBR_data"

# Set a safety limit (Set to None for unlimited, or an integer like 5)
MAX_FILES_TO_DOWNLOAD = None 

def sanitize_ftp_path(raw_path):
    if not raw_path:
        return ""
    clean_path = raw_path.replace("\\", "/").strip()
    clean_path = re.sub(r"^.*?/avago/FTP/EBR_data/", "", clean_path, flags=re.IGNORECASE)
    clean_path = clean_path.lstrip("/")
    return clean_path

def sanitize_folder_name(name):
    """Sanitize maskID to make sure it's a valid Windows folder name."""
    if not name:
        return "Unknown_MaskID"
    # Remove invalid Windows filename characters: \ / : * ? " < > |
    clean = re.sub(r'[\\/:*?"<>|]', '', name).strip()
    return clean if clean else "Unknown_MaskID"

def get_ftp_targets_from_csvs():
    """
    Reads all CSVs and pairs each clean FTP Path with its corresponding maskID (Device).
    Returns a set of tuples: (mask_id, clean_ftp_path)
    """
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
                        mask_id = sanitize_folder_name(rows[1][1].strip()) # Column 2 (Device / maskID)
                        raw_path = rows[1][9].strip()                     # Column 10 (Path)
                        clean_path = sanitize_ftp_path(raw_path)
                        
                        if clean_path:
                            targets.add((mask_id, clean_path))
            except Exception as e:
                print(f"Error reading {file}: {e}")
    return targets

def download_from_ftp(targets):
    print(f"Connecting to {FTP_HOST}...")
    ftp = FTP(FTP_HOST)
    ftp.login(user=FTP_USER, passwd=FTP_PASS)
    print("Logged in successfully.")

    downloaded_count = 0

    for mask_id, target in targets:
        if MAX_FILES_TO_DOWNLOAD and downloaded_count >= MAX_FILES_TO_DOWNLOAD:
            print(f"\nReached maximum download limit ({MAX_FILES_TO_DOWNLOAD} files). Stopping.")
            break

        # Create target subfolder: G:\My Drive\FTP data\<maskID>
        mask_folder_path = os.path.join(BASE_DOWNLOAD_DIR, mask_id)
        os.makedirs(mask_folder_path, exist_ok=True)

        full_ftp_path = f"{BASE_FTP_PATH}/{target}".replace("//", "/")
        print(f"\nProcessing target for MaskID [{mask_id}]: {full_ftp_path}")

        try:
            parent_dir = os.path.dirname(full_ftp_path)
            target_name = os.path.basename(full_ftp_path)

            ftp.cwd(parent_dir)
            files_in_dir = ftp.nlst()

            if target_name in files_in_dir:
                local_file_path = os.path.join(mask_folder_path, target_name)
                if not os.path.exists(local_file_path):
                    print(f"Downloading file to {mask_id}/: {target_name}...")
                    with open(local_file_path, "wb") as f:
                        ftp.retrbinary(f"RETR {target_name}", f.write)
                    print(f"Saved to {local_file_path}")
                    downloaded_count += 1
                else:
                    print(f"File already exists in {mask_id}/: {target_name}")
            else:
                ftp.cwd(full_ftp_path)
                folder_files = ftp.nlst()
                for f_name in folder_files:
                    if MAX_FILES_TO_DOWNLOAD and downloaded_count >= MAX_FILES_TO_DOWNLOAD:
                        print(f"\nReached maximum download limit ({MAX_FILES_TO_DOWNLOAD} files). Stopping.")
                        break

                    local_file_path = os.path.join(mask_folder_path, f_name)
                    if not os.path.exists(local_file_path):
                        print(f"Downloading to {mask_id}/: {f_name}...")
                        with open(local_file_path, "wb") as f:
                            ftp.retrbinary(f"RETR {f_name}", f.write)
                        print(f"Saved to {local_file_path}")
                        downloaded_count += 1
                    else:
                        print(f"File already exists in {mask_id}/: {f_name}")

        except Exception as e:
            print(f"Failed to process target {target}: {e}")

    ftp.quit()
    print(f"\nFTP Download Task Finished. Total new files downloaded: {downloaded_count}")

if __name__ == "__main__":
    targets = get_ftp_targets_from_csvs()
    print(f"Found {len(targets)} unique (maskID, path) targets to pull.")
    if targets:
        download_from_ftp(targets)