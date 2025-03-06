import os
import socket
import time  
from Crypto.Cipher import AES
from tqdm import tqdm  # Import tqdm for progress bar

# Create and connect client socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 9000))

# Key and nonce for encryption
key = b"L!M&oun!M0@d8745"  
nonce = b"M0@d8745L!M&oun!"  
cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)

# Define file details
file_path = "Rapport_1_FOTA 2.pdf"
file_size = os.path.getsize(file_path)
file_name_tos_send = "recieved_file.pdf"

# Encrypt file name and send it
encrypted_file_name = cipher.encrypt(file_name_tos_send.encode())
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
