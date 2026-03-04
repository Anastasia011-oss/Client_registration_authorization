import socket
import threading
import os
import hashlib

HOST = '127.0.0.1'
PORT = 5001
FILE_NAME = "users.txt"
PHOTO_DIR = "user_photos"

if not os.path.exists(PHOTO_DIR):
    os.makedirs(PHOTO_DIR)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(login, password):
    if not os.path.exists(FILE_NAME):
        open(FILE_NAME, "w").close()

    with open(FILE_NAME, "r") as f:
        for line in f:
            l, p_hash = line.strip().split(" ")
            if l == login:
                return "USER_EXISTS"

    password_hash = hash_password(password)

    with open(FILE_NAME, "a") as f:
        f.write(f"{login} {password_hash}\n")

    return "REGISTER_SUCCESS"

def login_user(login, password):
    if not os.path.exists(FILE_NAME):
        return "NO_USERS"

    password_hash = hash_password(password)

    with open(FILE_NAME, "r") as f:
        for line in f:
            l, p_hash = line.strip().split(" ")
            if l == login and p_hash == password_hash:
                return "LOGIN_SUCCESS"

    return "LOGIN_FAILED"

def handle_client(conn, addr):
    print("Client connected:", addr)

    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break

            parts = data.split(" ")
            command = parts[0]

            if command == "REGISTER":
                login = parts[1]
                password = parts[2]
                response = register_user(login, password)
                conn.send(response.encode())

            elif command == "LOGIN":
                login = parts[1]
                password = parts[2]
                response = login_user(login, password)
                conn.send(response.encode())

            elif command == "UPLOAD_PHOTO":
                login = parts[1]
                size = int(parts[2])

                filepath = os.path.join(PHOTO_DIR, f"{login}.jpg")
                conn.send("READY".encode())

                with open(filepath, "wb") as f:
                    received = 0
                    while received < size:
                        file_data = conn.recv(1024)
                        f.write(file_data)
                        received += len(file_data)

                conn.send("UPLOAD_SUCCESS".encode())

            elif command == "GET_PHOTO":
                login = parts[1]
                filepath = os.path.join(PHOTO_DIR, f"{login}.jpg")

                if os.path.exists(filepath):
                    size = os.path.getsize(filepath)
                    conn.send(f"PHOTO {size}".encode())
                    conn.recv(1024)

                    with open(filepath, "rb") as f:
                        while True:
                            file_data = f.read(1024)
                            if not file_data:
                                break
                            conn.send(file_data)
                else:
                    conn.send("NO_PHOTO".encode())

        except:
            break

    conn.close()
    print("Client disconnected:", addr)

print("Server started...")

while True:
    conn, addr = server.accept()
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()