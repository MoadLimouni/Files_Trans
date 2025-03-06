import socket
import os
from Crypto.Cipher import AES

# key and nonce for decrypting 
key = b"TheNeuralninekey"
nonce =b"TheNeuralnineNCE"

# Define the folder where received files should be saved
folder_location = "./reciev/"  

# Create the folder if it doesn't exist
os.makedirs(folder_location, exist_ok=True)

cipher = AES.new(key,AES.MODE_EAX,nonce)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 9000))
server.listen()
print("Server is listening on port 9000...")

client, addr = server.accept()
print(f"Connection established with {addr}")

# Receive file name
file_name = client.recv(1024).decode().strip()
print(f"Receiving file: {file_name}")

# Receive file size
try:
    file_size = int(client.recv(1024).decode().strip())
    print(f"File size: {file_size} bytes")
except ValueError:
    print("Error: Could not parse file size.")
    client.close()
    server.close()
    exit()

# Save the file in the receiver's repository
file_path = os.path.join(folder_location, file_name)

# Receive file data and write to the correct directory
with open(file_path, "wb") as file:
    received_size = 0
    while received_size < file_size:
        data = client.recv(1024)
        if not data:
            break
        file.write(data)
        received_size += len(data)

print(f"File received and saved as {file_path}")

client.close()
server.close()
