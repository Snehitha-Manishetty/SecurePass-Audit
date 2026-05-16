import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import json
import hashlib
import base64
import os
import sys
import time

# Load Rainbow Table

class RainbowTable:
    def __init__(self, table_files):
        self.table_files = table_files
        self.rainbow_table = self.load_rainbow_tables()

    def load_rainbow_tables(self):
        combined_table = {}
        for file in self.table_files:
            file_path = self.resource_path(file)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        table = json.load(f)
                        # normalize keys (strip whitespace) to make lookups forgiving
                        for k, v in table.items():
                            if isinstance(k, str):
                                combined_table[k.strip()] = v
                            else:
                                combined_table[k] = v
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON {file_path}: {e}")
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
            else:
                print(f"File not found: {file_path}")
        return combined_table

    @staticmethod
    def resource_path(relative_path):
        # Prefer PyInstaller _MEIPASS when available, otherwise use the module directory
        base_path = getattr(sys, '_MEIPASS', None)
        if not base_path:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, relative_path)

# Window
class RainbowAttackGUI:
    def __init__(self, root, table_files=None):
        self.root = root
        self.root.title("Rainbow Table Attack")
        self.root.geometry("500x300")

        # Rainbow table data file(s)
        if table_files is None:
            table_files = ['rainbow_table.json']
        self.rainbow_table = RainbowTable(table_files).rainbow_table

        self.create_widgets()

    def create_widgets(self):
        
        self.hash_value_label = ctk.CTkLabel(self.root, text="Enter Hash Value:")   # Label & Entry for hash value
        self.hash_value_label.pack(padx=10, pady=(20, 5), anchor='w')
        
        self.hash_value_entry = ctk.CTkEntry(self.root, width=300)
        self.hash_value_entry.pack(padx=10, pady=5, fill='x', expand=True)
        
        self.button_frame = ctk.CTkFrame(self.root)  # Frame for buttons
        self.button_frame.pack(pady=10)

        self.attack_button = ctk.CTkButton(self.button_frame, text="Start Attack", command=self.start_attack)  # Button to start the attack
        self.attack_button.pack(side='left', padx=5)

        self.clear_button = ctk.CTkButton(self.button_frame, text="Clear", command=self.clear_process)         # Button to clear the process
        self.clear_button.pack(side='left', padx=5)

        self.result_label = ctk.CTkLabel(self.root, text="Result:")         # Result display
        self.result_label.pack(padx=10, pady=5, anchor='w')

        self.result = tk.StringVar()
        self.result_display = ctk.CTkLabel(self.root, textvariable=self.result, width=300)
        self.result_display.pack(padx=10, pady=5, fill='x', expand=True)

    def start_attack(self):   # Function to Start attack
        hash_value = self.hash_value_entry.get()
        self.result.set("")

        if not hash_value:
            messagebox.showwarning("Input Error", "Please enter a hash value.")
            return

        start_time = time.time()   # Timer Start
        match = self.rainbow_table.get(hash_value, None)
        end_time = time.time()  # Stop TImer
        time_taken = end_time - start_time

        if match:
            original_text, hash_type = match
            self.result.set(f"Match found: {original_text} (Hash type: {hash_type})\nTime taken: {time_taken:.2f} seconds")  # Results
        else:
            self.result.set(f"No match found.\nTime taken: {time_taken:.2f} seconds")

    def clear_process(self):   # CLear Button
        """
        Clears the hash value entry and result display.
        """
        self.hash_value_entry.delete(0, tk.END)
        self.result.set("")

def main():
    # Allow optional command-line arg: path to a rainbow_table.json file
    table_files = None
    if len(sys.argv) > 1:
        # accept one or more file paths
        table_files = []
        for arg in sys.argv[1:]:
            table_files.append(arg)

    root = ctk.CTk()
    app = RainbowAttackGUI(root, table_files=table_files)
    root.mainloop()


if __name__ == "__main__":
    main()
