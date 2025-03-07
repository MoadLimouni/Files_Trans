import os
import socket
import time
import hashlib
from Crypto.Cipher import AES
from tqdm import tqdm  


HOST = "localhost"
PORT = 9000
BUFFER_SIZE = 1024  
KEY_FILE_PATH = "./key.txt"
NONCE_FILE_PATH = "./nonce.txt"
FILE_PATH = "Rapport_1_FOTA 2.pdf"

def read_file_safely(file_path):
    """Read and return file contents safely, handling errors."""
    try:
        with open(file_path, "rb") as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ Error: The file '{file_path}' was not found.")
        exit(1)
    except PermissionError:
        print(f"❌ Error: Permission denied when accessing '{file_path}'.")
        exit(1)
    except Exception as e:
        print(f"❌ Unexpected error reading '{file_path}': {e}")
        exit(1)

try:
    # Read encryption key and nonce
    key = read_file_safely(KEY_FILE_PATH)
    nonce = read_file_safely(NONCE_FILE_PATH)

    # Validate key length for AES
    if len(key) not in (16, 24, 32):
        raise ValueError("Invalid AES key length. Key must be 16, 24, or 32 bytes.")

    # Create AES cipher
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)

    # Verify file existence
    if not os.path.exists(FILE_PATH):
        raise FileNotFoundError(f"The file '{FILE_PATH}' does not exist.")

    # Get file details
    file_size = os.path.getsize(FILE_PATH)
    file_name_to_send = os.path.basename(FILE_PATH)

    # Compute file hash
    with open(FILE_PATH, "rb") as f:
        original_hash = hashlib.sha256(f.read()).hexdigest()

    # Create and connect to the server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(10)  # Set a timeout for connection attempts
    try:
        client.connect((HOST, PORT))
    except socket.timeout:
        print("❌ Connection timed out. Is the server running?")
        exit(1)
    except ConnectionRefusedError:
        print("❌ Connection refused. Ensure the server is online and the port is correct.")
        exit(1)

    # Encrypt and send the file hash
    client.send(cipher.encrypt(original_hash.encode()))
    time.sleep(0.1)

    # Encrypt and send the file name
    client.send(cipher.encrypt(file_name_to_send.encode()))
    time.sleep(0.1)

    # Encrypt and send the file size
    client.send(cipher.encrypt(str(file_size).encode()))
    time.sleep(0.1)

    # Encrypt and send file content with progress bar
    with open(FILE_PATH, "rb") as file, tqdm(total=file_size, unit="B", unit_scale=True, desc="Sending") as pbar:
        while chunk := file.read(BUFFER_SIZE):  
            client.send(cipher.encrypt(chunk))
            pbar.update(len(chunk))

    # Send encrypted end signal
    client.send(cipher.encrypt(b"<END>"))

    print("\n✅ File sent successfully.")

except ValueError as ve:
    print(f"❌ Value Error: {ve}")
except FileNotFoundError as fnf:
    print(f"❌ File Error: {fnf}")
except PermissionError:
    print("❌ Permission Error: Check your file access rights.")
except socket.error as se:
    print(f"❌ Socket Error: {se}")
except Exception as e:
    print(f"❌ Unexpected Error: {e}")
finally:
    try:
        client.close()
        print("🔌 Connection closed.")
    except NameError:
        pass  

