import os
import sys
import shutil
import subprocess
import threading
import webbrowser
import customtkinter as ctk
from tkinter import filedialog, messagebox
import queue
import tkinter as tk

# Global variables
process = None
output_queue = queue.Queue()

# Function to select handshake file
def select_handshake_file():
    handshake_file = filedialog.askopenfilename(
        title="Select Handshake File",
        filetypes=[("Handshake Files", "*.cap *.pcapng *.hccapx"), ("All Files", "*.*")]
    )
    handshake_entry.delete(0, ctk.END)
    handshake_entry.insert(0, handshake_file)

# Function to select wordlist file
def select_wordlist_file():
    wordlist_file = filedialog.askopenfilename(
        title="Select Wordlist File",
        filetypes=[("Wordlist Files", "*.txt"), ("All Files", "*.*")]
    )
    wordlist_entry.delete(0, ctk.END)
    wordlist_entry.insert(0, wordlist_file)

# Function to run aircrack-ng in a separate thread
def run_aircrack():
    global process

    handshake_file = handshake_entry.get()
    wordlist_file = wordlist_entry.get()

    # Check if both files are selected
    if not handshake_file or not wordlist_file:
        messagebox.showwarning("Input Error", "Please select both handshake and wordlist files.")
        return

    # Resolve which aircrack-ng command to run.
    aircrack_exec = ''
    try:
        aircrack_exec = aircrack_entry.get().strip()
    except Exception:
        aircrack_exec = ''

    if aircrack_exec:
        # User provided a path to an executable
        if not os.path.isfile(aircrack_exec):
            messagebox.showerror("Missing file", f"The provided aircrack-ng executable was not found: {aircrack_exec}")
            return
        aircrack_cmd = aircrack_exec
    else:
        # Try to find aircrack-ng on PATH
        which_path = shutil.which("aircrack-ng")
        if which_path:
            aircrack_cmd = which_path
        else:
            try:
                open_now = messagebox.askyesno(
                    "Missing Dependency",
                    "aircrack-ng is not installed or not found in PATH.\n"
                    "Would you like to open the official download page now?"
                )
                if open_now:
                    webbrowser.open("https://www.aircrack-ng.org/downloads.html")
            except Exception:
                messagebox.showerror("Error", "aircrack-ng is not installed or not found in PATH.")
            return

    # Clear 
    try:
        result_text.delete(1.0, tk.END)
    except Exception:
        try:
            result_text.delete(1.0, ctk.END)
        except Exception:
            pass
    password_label.configure(text="")  # Clear password display

    # Disable buttons
    crack_button.configure(state=ctk.DISABLED)
    cancel_button.configure(state=ctk.NORMAL)

    # Start the aircrack-ng process in a separate thread using resolved command
    thread = threading.Thread(target=aircrack_process, args=(handshake_file, wordlist_file, aircrack_cmd))
    thread.start()

    # Continuously check the output queue for updates
    check_output_queue()

# Function to handle the aircrack-ng process
def aircrack_process(handshake_file, wordlist_file, aircrack_cmd="aircrack-ng"):
    global process

    try:
        # Run aircrack-ng command
        command = [aircrack_cmd, "-w", wordlist_file, handshake_file]
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except FileNotFoundError:
            output_queue.put("ERROR: 'aircrack-ng' not found when attempting to execute command. Ensure it is installed and on PATH.")
            process = None
        except Exception as e:
            output_queue.put(f"ERROR: Failed to start aircrack-ng: {e}")
            process = None

        # Read the output line by line
        if process is not None and process.stdout is not None:
            for line in iter(process.stdout.readline, ''):
                if line:
                    output_queue.put(line)  # Add the output to the queue

            process.stdout.close()
            process.wait()

            if process.returncode != 0:
                output_queue.put("ERROR: Failed to crack the password or no password found.")

    except Exception as e:
        output_queue.put(f"ERROR: An error occurred: {e}")

    finally:
        process = None
        output_queue.put("DONE")

# Function to check the output queue and update the GUI
def check_output_queue():
    try:
        while True:
            line = output_queue.get_nowait()  # Get the next line from the queue

            if line.startswith("ERROR:"):
                error_message = line.split(":", 1)[1]
                messagebox.showerror("Error", error_message)

            elif "KEY FOUND!" in line:
                # Extract and display the password
                import re
                match = re.search(r'KEY FOUND! \[ (.+) \]', line)
                if match:
                    password = match.group(1)
                    display_password(password)
                    return  # Stop checking queue

            elif line == "DONE":
                # Re-enable buttons
                crack_button.configure(state=ctk.NORMAL)
                cancel_button.configure(state=ctk.DISABLED)
                return

            else:
                try:
                    result_text.insert(tk.END, line)
                    result_text.see(tk.END)  # Auto-scroll to the end
                except Exception:
                    # If CTkTextbox isn't available, fall back to Tk Text widget methods
                    try:
                        result_text.insert(tk.END, line)
                    except Exception:
                        pass

    except queue.Empty:
        root.after(100, check_output_queue)

# Function to handle password display and message box
def display_password(password):
    password_label.configure(text=f"Password: {password}")
    messagebox.showinfo("Password Found", f"The cracked password is: {password}")

# Function to clear the process
def clear_process():
    global process
    if process is not None:
        try:
            process.terminate()
            process = None
        except Exception as e:
            messagebox.showerror("Error", f"Failed to terminate the process: {e}")
    
    # Clear results and reset UI elements
    result_text.delete(1.0, ctk.END)
    password_label.configure(text="")
    handshake_entry.delete(0, ctk.END)
    wordlist_entry.delete(0, ctk.END)
    crack_button.configure(state=ctk.NORMAL)
    cancel_button.configure(state=ctk.DISABLED)

# Function to cancel the cracking process
def cancel_aircrack():
    global process
    if process is not None:
        try:
            process.terminate()
            process = None
            clear_process()
            messagebox.showinfo("Cancelled", "Cracking process has been cancelled.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to cancel the process: {e}")
    else:
        messagebox.showwarning("Warning", "No running process to cancel.")

# Main window
root = ctk.CTk()
root.title("Wi-Fi Password Cracker")
root.geometry("700x400")
root.resizable(False, False)

# Theme and color
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Handshake file selection
handshake_frame = ctk.CTkFrame(root)
handshake_frame.pack(pady=5)

handshake_label = ctk.CTkLabel(handshake_frame, text="Select Handshake File:")
handshake_label.pack(side=ctk.LEFT, padx=5)

handshake_entry = ctk.CTkEntry(handshake_frame, width=300)
handshake_entry.pack(side=ctk.LEFT, padx=5)

handshake_button = ctk.CTkButton(handshake_frame, text="Browse", command=select_handshake_file)
handshake_button.pack(side=ctk.LEFT, padx=5)

# Wordlist file selection
wordlist_frame = ctk.CTkFrame(root)
wordlist_frame.pack(pady=5)

wordlist_label = ctk.CTkLabel(wordlist_frame, text="Select Wordlist File:")
wordlist_label.pack(side=ctk.LEFT, padx=5)

wordlist_entry = ctk.CTkEntry(wordlist_frame, width=300)
wordlist_entry.pack(side=ctk.LEFT, padx=5)

wordlist_button = ctk.CTkButton(wordlist_frame, text="Browse", command=select_wordlist_file)
wordlist_button.pack(side=ctk.LEFT, padx=5)

# Aircrack executable selection (optional)
aircrack_frame = ctk.CTkFrame(root)
aircrack_frame.pack(pady=5)

aircrack_label = ctk.CTkLabel(aircrack_frame, text="aircrack-ng executable (optional):")
aircrack_label.pack(side=ctk.LEFT, padx=5)

aircrack_entry = ctk.CTkEntry(aircrack_frame, width=300)
aircrack_entry.pack(side=ctk.LEFT, padx=5)

def select_aircrack_file():
    exe_file = filedialog.askopenfilename(
        title="Select aircrack-ng executable",
        filetypes=[("Executable", "*.exe;*"), ("All Files", "*")]
    )
    if exe_file:
        aircrack_entry.delete(0, ctk.END)
        aircrack_entry.insert(0, exe_file)

aircrack_button = ctk.CTkButton(aircrack_frame, text="Browse", command=select_aircrack_file)
aircrack_button.pack(side=ctk.LEFT, padx=5)

# Buttons frame
buttons_frame = ctk.CTkFrame(root)
buttons_frame.pack(pady=10)

# Start cracking button
crack_button = ctk.CTkButton(buttons_frame, text="Start Cracking", command=run_aircrack)
crack_button.pack(side=ctk.LEFT, padx=5)

# Cancel button
cancel_button = ctk.CTkButton(buttons_frame, text="Cancel", command=cancel_aircrack, state=ctk.DISABLED)
cancel_button.pack(side=ctk.LEFT, padx=5)

# Clear button
clear_button = ctk.CTkButton(buttons_frame, text="Clear", command=clear_process)
clear_button.pack(side=ctk.LEFT, padx=5)
 
# Helper button to open the aircrack-ng downloads page
def open_aircrack_downloads():
    try:
        webbrowser.open("https://www.aircrack-ng.org/downloads.html")
    except Exception as e:
        messagebox.showerror("Error", f"Unable to open web browser: {e}")

get_button = ctk.CTkButton(buttons_frame, text="Get aircrack-ng", command=open_aircrack_downloads)
get_button.pack(side=ctk.LEFT, padx=5)

# Result
try:
    # Newer versions of customtkinter provide CTkTextbox
    result_text = ctk.CTkTextbox(root, height=150, width=500)
    result_text.pack(pady=10)
except Exception:
    # Fallback to standard Tk Text widget when CTkTextbox is not available
    result_text = tk.Text(root, height=10, width=60)
    result_text.pack(pady=10)

# Cracked password
password_label = ctk.CTkLabel(root, text="", font=("Arial", 18, "bold"))
password_label.pack(pady=20)

def main():
    # Handle command line arguments if provided
    if len(sys.argv) > 2:
        handshake_entry.insert(0, sys.argv[1])  # First argument is the handshake file
        wordlist_entry.insert(0, sys.argv[2])   # Second argument is the wordlist
    root.mainloop()


if __name__ == "__main__":
    main()
