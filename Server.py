import socket
import os
import hashlib
from Crypto.Cipher import AES
from tqdm import tqdm  


HOST = "localhost"
PORT = 9000
BUFFER_SIZE = 1024
KEY_FILE_PATH = "./key_server.txt"
NONCE_FILE_PATH = "./nonce_server.txt"
FOLDER_LOCATION = "../reciev"
os.makedirs(FOLDER_LOCATION, exist_ok=True)

def read_file_safely(file_path):
    """Safely reads a file and returns its contents."""
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

    # Validate AES key length
    if len(key) not in (16, 24, 32):
        raise ValueError("Invalid AES key length. Key must be 16, 24, or 32 bytes.")

    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)

    # Set up server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"⏭ Server is listening on port {PORT}...")

    client, addr = server.accept()
    print(f"✅ Connection established with {addr}")

    # Receive and decrypt the original file hash
    encrypted_original_hash = client.recv(BUFFER_SIZE)
    original_hash = cipher.decrypt(encrypted_original_hash).decode().strip()

    # Receive and decrypt file name
    encrypted_file_name = client.recv(BUFFER_SIZE)
    file_name = cipher.decrypt(encrypted_file_name).decode().strip()
    print(f"⏭ Receiving file: {file_name}")

    # Receive and decrypt file size
    try:
        encrypted_file_size = client.recv(BUFFER_SIZE)
        file_size = int(cipher.decrypt(encrypted_file_size).decode().strip())
        print(f"⏭ File size: {file_size} bytes")
    except ValueError:
        print("❌ Error: Could not parse file size.")
        exit(1)

    # Save file to the correct directory
    file_path = os.path.join(FOLDER_LOCATION, file_name)

    # Receive and decrypt file data with progress bar
    try:
        received_size = 0
        with open(file_path, "wb") as file, tqdm(total=file_size, unit="B", unit_scale=True, desc="Receiving") as pbar:
            while received_size < file_size:
                data = client.recv(BUFFER_SIZE)
                if not data:
                    break
                decrypted_data = cipher.decrypt(data)
                
                # Stop if the "<END>" message is received
                if decrypted_data == b"<END>":
                    break
                
                file.write(decrypted_data)
                received_size += len(decrypted_data)
                pbar.update(len(decrypted_data))

        print(f"✅ File received and saved as: {file_name}")
    except Exception as e:
        print(f"❌ Error: Could not receive or decrypt data: {e}")
        exit(1)

    # Compute hash of the received file
    with open(file_path, "rb") as f:
        received_hash = hashlib.sha256(f.read()).hexdigest()

    # Compare hashes for integrity check
    if received_hash == original_hash:
        print("✅ File integrity check passed!")
    else:
        print("❌ File integrity check failed!")

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
    # Ensure cleanup
    try:
        client.close()
        server.close()
        print("🔌 Connection closed.")
    except NameError:
        pass  
