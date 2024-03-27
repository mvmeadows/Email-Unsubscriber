import tkinter as tk
from tkinter import ttk
from email_unsubscriber import display_sender_stats

def analyze_emails_and_display():
    display_sender_stats()

def main():
    root = tk.Tk()
    root.title("Email Unsubscriber")

    label = ttk.Label(root, text="Welcome to Email Unsubscriber!")
    label.pack(pady=10)

    button_analyze = ttk.Button(root, text="Analyze Emails", command=analyze_emails_and_display)
    button_analyze.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
