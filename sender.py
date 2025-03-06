import os
import socket
import time  
from Crypto.Cipher import AES


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 9000))

# key and nonce for encrypting
key = b"TheNeuralninekey"
nonce =b"TheNeuralnineNCE"
cipher = AES.new(key,AES.MODE_EAX,nonce)

file_path = "filetosend.txt"
file_size= os.path.getsize(file_path)
encrypted_file_size = cipher.encrypt(file_size)
enb=encrypted_file_size.to_bytes(8, 'big') # atttttention here

# Send file name

file_name="recieved_file.txt" 
encrypted_file_name=cipher.encrypt(file_name)
client.send(encrypted_file_name.encode())
time.sleep(0.1)  # Short delay to avoid mixed messages

# Send file size
client.send(str(encrypted_file_size).encode())

time.sleep(0.1)  

# Send file content
with open(file_path, "rb") as file:
    data = file.read(1024)
    while data:
        encrypted_data=cipher.encrypt(data)
        client.send(encrypted_data.tobyte)
        data = file.read(1024)

client.send(b"<END>")  
print(data)
client.close()
