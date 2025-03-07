import os
import socket
import time
import hashlib
from Crypto.Cipher import AES
from tqdm import tqdm  

# Create and connect client socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "localhost"
port = 9000
client.connect((host, port))


# Define file details
key_file_path = "./key.txt"
nonce_file_path = "./nonce.txt"

# Read the key and nonce files
with open(key_file_path, "rb") as f:
    key = f.read()
with open(nonce_file_path, "rb") as f:
    nonce = f.read()

# Create a cipher using the key and nonce
cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)

# Define file details
file_path = "Rapport_1_FOTA 2.pdf"
file_size = os.path.getsize(file_path)
file_name_to_send = os.path.basename(file_path)

# Compute file hash
with open(file_path, "rb") as f:
    original_hash = hashlib.sha256(f.read()).hexdigest()

# Encrypt and send the file hash
encrypted_hash = cipher.encrypt(original_hash.encode())
client.send(encrypted_hash)
time.sleep(0.1)

# Encrypt file name and send it
encrypted_file_name = cipher.encrypt(file_name_to_send.encode())
client.send(encrypted_file_name)
time.sleep(0.1)

# Encrypt file size and send it
encrypted_file_size = cipher.encrypt(str(file_size).encode())
client.send(encrypted_file_size)
time.sleep(0.1)

# Encrypt and send file content with a progress bar
with open(file_path, "rb") as file, tqdm(total=file_size, unit="B", unit_scale=True, desc="Sending") as pbar:
    while True:
        data = file.read(1024)
        if not data:
            break
        encrypted_data = cipher.encrypt(data)
        client.send(encrypted_data)
        pbar.update(len(data))

# Send encrypted end signal
encrypted_end = cipher.encrypt(b"<END>")
client.send(encrypted_end)

print("\nFile sent successfully.")
client.close()
