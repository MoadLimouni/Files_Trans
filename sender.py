import os
import socket
import time  
from Crypto.Cipher import AES

# Create and connect client socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 9000))

# Key and nonce for encryption
key = b"L!M&oun!M0@d8745"  
nonce = b"M0@d8745L!M&oun!"  
cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)

# Define file details
file_path = "filetosend.txt"
file_size = os.path.getsize(file_path)
file_name = "recieved_file.txt"

# Encrypt file name and send it
encrypted_file_name = cipher.encrypt(file_name.encode())
client.send(encrypted_file_name)
time.sleep(0.1)

# Encrypt file size and send it
encrypted_file_size = cipher.encrypt(str(file_size).encode())
client.send(encrypted_file_size)
time.sleep(0.1)

# Encrypt and send file content
with open(file_path, "rb") as file:
    while True:
        data = file.read(1024)
        if not data:
            break
        encrypted_data = cipher.encrypt(data)
        client.send(encrypted_data)

# Send encrypted end signal
encrypted_end = cipher.encrypt(b"<END>")
client.send(encrypted_end)

print("File sent successfully.")
client.close()
