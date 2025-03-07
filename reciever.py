import socket
import os
from Crypto.Cipher import AES

# Define file details
key_file_path = "./key.txt"
nonce_file_path = "./nonce.txt"

# Read the key and nonce files 
with open(key_file_path, "rb") as f:
    key = f.read()
with open(nonce_file_path, "rb") as f:
    nonce = f.read()


cipher = AES.new(key, AES.MODE_EAX, nonce=nonce) 

# Define folder where received files should be saved
folder_location = "./reciev/"
os.makedirs(folder_location, exist_ok=True)

# Set up server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 9000))
server.listen()
print("Server is listening on port 9000...")

client, addr = server.accept()
print(f"Connection established with {addr}")

# Receive and decrypt file name
encrypted_file_name = client.recv(1024)
file_name = cipher.decrypt(encrypted_file_name).decode().strip()
print(f"Receiving file: {file_name}")

# Receive and decrypt file size
try:
    encrypted_file_size = client.recv(1024)
    file_size = int(cipher.decrypt(encrypted_file_size).decode().strip())
    print(f"File size: {file_size} bytes")
except ValueError:
    print("Error: Could not parse file size.")
    client.close()
    server.close()
    exit()

# Save file to the correct directory
file_path = os.path.join(folder_location, file_name)

# Receive and decrypt file data
received_size = 0
with open(file_path, "wb") as file:
    while received_size < file_size:
        data = client.recv(1024)
        if not data:
            break
        decrypted_data = cipher.decrypt(data)
        
        # Stop if the "<END>" message is received
        if decrypted_data == b"<END>":
            break
        
        file.write(decrypted_data)
        received_size += len(decrypted_data)

print(f"File received and saved as {file_path}")

client.close()
server.close()
