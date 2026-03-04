import socket
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import os

HOST = '127.0.0.1'
PORT = 5001

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

current_user = None

def send_request(message):
    client.send(message.encode())
    return client.recv(1024).decode()

def show_frame(frame):
    frame_menu.pack_forget()
    frame_register.pack_forget()
    frame_login.pack_forget()
    frame_profile.pack_forget()
    frame.pack(pady=20)

def register():
    login = reg_login_entry.get()
    password = reg_password_entry.get()

    if not login or not password:
        messagebox.showerror("Ошибка", "Введите логин и пароль")
        return

    response = send_request(f"REGISTER {login} {password}")

    if response == "REGISTER_SUCCESS":
        messagebox.showinfo("Успех", "Регистрация успешна")
        show_frame(frame_menu)
    else:
        messagebox.showerror("Ошибка", "Пользователь уже существует")

def login():
    global current_user

    login_val = log_login_entry.get()
    password = log_password_entry.get()

    if not login_val or not password:
        messagebox.showerror("Ошибка", "Введите логин и пароль")
        return

    response = send_request(f"LOGIN {login_val} {password}")

    if response == "LOGIN_SUCCESS":
        current_user = login_val
        show_frame(frame_profile)
        load_photo()
    else:
        messagebox.showerror("Ошибка", "Неверный логин или пароль")

def choose_photo():
    filepath = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg *.png")]
    )
    if not filepath:
        return

    size = os.path.getsize(filepath)
    client.send(f"UPLOAD_PHOTO {current_user} {size}".encode())

    client.recv(1024)

    with open(filepath, "rb") as f:
        while True:
            data = f.read(1024)
            if not data:
                break
            client.send(data)

    response = client.recv(1024).decode()

    if response == "UPLOAD_SUCCESS":
        messagebox.showinfo("Успех", "Фото загружено")
        load_photo()

def load_photo():
    client.send(f"GET_PHOTO {current_user}".encode())
    response = client.recv(1024).decode()

    if response.startswith("PHOTO"):
        size = int(response.split()[1])
        client.send("READY".encode())

        filepath = f"{current_user}_temp.jpg"

        with open(filepath, "wb") as f:
            received = 0
            while received < size:
                data = client.recv(1024)
                f.write(data)
                received += len(data)

        img = Image.open(filepath)
        img = img.resize((150, 150))
        photo = ImageTk.PhotoImage(img)

        photo_label.config(image=photo)
        photo_label.image = photo

root = tk.Tk()
root.title("Авторизация")
root.geometry("300x350")

frame_menu = tk.Frame(root)
tk.Button(frame_menu, text="Регистрация", command=lambda: show_frame(frame_register)).pack(pady=10)
tk.Button(frame_menu, text="Авторизация", command=lambda: show_frame(frame_login)).pack(pady=10)

frame_register = tk.Frame(root)
tk.Label(frame_register, text="Регистрация").pack()
tk.Label(frame_register, text="Логин").pack()
reg_login_entry = tk.Entry(frame_register)
reg_login_entry.pack()
tk.Label(frame_register, text="Пароль").pack()
reg_password_entry = tk.Entry(frame_register, show="*")
reg_password_entry.pack()
tk.Button(frame_register, text="Зарегистрироваться", command=register).pack(pady=5)
tk.Button(frame_register, text="Назад", command=lambda: show_frame(frame_menu)).pack()

frame_login = tk.Frame(root)
tk.Label(frame_login, text="Авторизация").pack()
tk.Label(frame_login, text="Логин").pack()
log_login_entry = tk.Entry(frame_login)
log_login_entry.pack()
tk.Label(frame_login, text="Пароль").pack()
log_password_entry = tk.Entry(frame_login, show="*")
log_password_entry.pack()
tk.Button(frame_login, text="Войти", command=login).pack(pady=5)
tk.Button(frame_login, text="Назад", command=lambda: show_frame(frame_menu)).pack()

frame_profile = tk.Frame(root)
photo_label = tk.Label(frame_profile)
photo_label.pack(pady=10)
tk.Button(frame_profile, text="Выбрать фото", command=choose_photo).pack()
tk.Button(frame_profile, text="Назад", command=lambda: show_frame(frame_menu)).pack()

show_frame(frame_menu)
root.mainloop()