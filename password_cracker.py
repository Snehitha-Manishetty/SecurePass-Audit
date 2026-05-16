from customtkinter import *
import customtkinter
import os
import webbrowser
import pathlib
from PIL import Image, ImageTk
import tkinter.messagebox as tk_messagebox
import threading
import subprocess
import sys

# Window
app = customtkinter.CTk()
app.title("Password Cracker")
app.geometry('945x630')
app.resizable(False, False)
set_appearance_mode('dark')

# Background Image
image_path = os.path.join(os.path.dirname(__file__), 'Background_image.png')
image = customtkinter.CTkImage(light_image=Image.open(image_path), size=(945,630))
image_label = customtkinter.CTkLabel(app, image=image, text="")
image_label.place(relx=0, rely=0)

# Project Info Button
def project_info():
    # Open ProjectInfo.html in a new browser tab using a file:// URL
    html_file = os.path.join(os.path.dirname(__file__), "ProjectInfo.html")
    try:
        file_url = pathlib.Path(html_file).as_uri()
        webbrowser.open_new_tab(file_url)
    except Exception:
        # Fallback: try OS default opener
        try:
            os.startfile(html_file)
        except Exception:
            print(f"Unable to open project info: {html_file}")

button_project_info = customtkinter.CTkButton(master=app, text="PROJECT INFO", bg_color="white", fg_color="#1c93d7", width=200, height=35,  font=("Arial", 17),
                                             hover_color="#00bf63", corner_radius=5, cursor="hand2", command=project_info)
button_project_info.place(x=372, y=290)

# Wordlist attack Button
def wordlist_attack():
    base_dir = os.path.dirname(__file__)
    python_file = os.path.join(base_dir, "wordlist.py")
    hash_file = os.path.join(base_dir, "hash.txt")
    rockyou = os.path.join(base_dir, "rockyou.txt")
    # Ensure files exist
    if not os.path.exists(hash_file):
        tk_messagebox.showerror("Missing file", f"hash.txt not found at: {hash_file}")
        return
    if not os.path.exists(rockyou):
        tk_messagebox.showerror("Missing file", f"rockyou.txt not found at: {rockyou}")
        return
    # Subprocess using the same interpreter and passing default files
    subprocess.Popen([sys.executable, python_file, hash_file, rockyou], creationflags=subprocess.CREATE_NO_WINDOW)

def wordlist_attack_thread():
    threading.Thread(target=wordlist_attack).start()

button_open_python = customtkinter.CTkButton(master=app, text="WORDLIST ATTACK", bg_color="white", fg_color="#1c93d7", width=250, height=35,  font=("Arial", 17),
                                            hover_color="#00bf63", corner_radius=5, cursor="hand2", command=wordlist_attack_thread)
button_open_python.place(x=200, y=350)


# Rainbow table Button
def rainbow_table_attack():
    base_dir = os.path.dirname(__file__)
    python_file = os.path.join(base_dir, "rainbow_table.py")
    json_file = os.path.join(base_dir, "rainbow_table.json")
    # Ensure the JSON file exists before launching
    if not os.path.exists(json_file):
        tk_messagebox.showerror("Missing data file", f"rainbow_table.json not found at: {json_file}")
        return
    # Subprocess using the same interpreter; pass the json path as an argument
    subprocess.Popen([sys.executable, python_file, json_file], creationflags=subprocess.CREATE_NO_WINDOW)

def rainbow_table_attack_thread():
    threading.Thread(target=rainbow_table_attack).start()

button_open_python = customtkinter.CTkButton(master=app, text="RAINBOW TABLE ATTACK", bg_color="white", fg_color="#1c93d7", width=250, height=35,  font=("Arial", 17),
                                            hover_color="#00bf63", corner_radius=5, cursor="hand2", command=rainbow_table_attack_thread)
button_open_python.place(x=495, y=350)


# Router Credentials Button
def router_creds():
    base_dir = os.path.dirname(__file__)
    python_file = os.path.join(base_dir, "router.py")
    if not os.path.exists(python_file):
        tk_messagebox.showerror("Missing file", f"router.py not found at: {python_file}")
        return
    # Subprocess using the same interpreter
    subprocess.Popen([sys.executable, python_file], creationflags=subprocess.CREATE_NO_WINDOW)

def router_creds_thread():
    threading.Thread(target=router_creds).start()

button_open_python = customtkinter.CTkButton(master=app, text="ROUTER DEFAULT CREDENTIALS", bg_color="white", fg_color="#1c93d7", width=300, height=35,  font=("Arial", 17),
                                            hover_color="#00bf63", corner_radius=5, cursor="hand2", command=router_creds_thread)
button_open_python.place(x=150, y=410)




# Website Bruteforce Button
def website_bruteforce():
    base_dir = os.path.dirname(__file__)
    python_file = os.path.join(base_dir, "website-login.py")
    website_creds = os.path.join(base_dir, "Website Login Credentials.txt")
    # Ensure file exists
    if not os.path.exists(python_file):
        tk_messagebox.showerror("Missing file", f"website-login.py not found at: {python_file}")
        return
    # Check if requests is available in the current interpreter
    try:
        import importlib
        spec = importlib.util.find_spec('requests')
        if spec is None:
            tk_messagebox.showerror("Missing dependency", "The 'requests' package is required by website-login.py. Install it in this Python environment.")
            return
    except Exception:
        # best-effort; continue to try to launch
        pass
    # Ensure credentials file exists and pass it as default wordlist
    if not os.path.exists(website_creds):
        tk_messagebox.showerror("Missing file", f"Website Login Credentials.txt not found at: {website_creds}")
        return
    # Subprocess using the same interpreter
    subprocess.Popen([sys.executable, python_file, '', website_creds], creationflags=subprocess.CREATE_NO_WINDOW)

def website_bruteforce_thread():
    threading.Thread(target=website_bruteforce).start()

button_open_python = customtkinter.CTkButton(master=app, text="WEBSITE LOGIN BRUTEFORCE", bg_color="white", fg_color="#1c93d7", width=350, height=35,  font=("Arial", 17),
                                            hover_color="#00bf63", corner_radius=5, cursor="hand2", command=website_bruteforce_thread)
button_open_python.place(x=298, y=470)

app.mainloop()