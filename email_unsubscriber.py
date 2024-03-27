import tkinter as tk
from tkinter import ttk, messagebox
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import webbrowser
import os
import re
from datetime import datetime
import json
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']
UNSUBSCRIBE_FILE = 'unsubscribed_senders.txt'
CLIENT_SECRETS_FILE = 'client_secrets.json'

def extract_unsubscribe_link(email_data):
    """Extracts the unsubscribe link from the email headers."""
    for header in email_data:
        if header['name'] == 'List-Unsubscribe':
            unsubscribe_links = re.findall(r'<(.*?)>', header['value'])
            return unsubscribe_links
    return None

def initiate_oauth_flow():
    """Initiates the OAuth flow to obtain credentials and saves them to client_secrets.json."""
    if not os.path.exists(CLIENT_SECRETS_FILE):
        # If client_secrets.json does not exist, initiate OAuth flow to create it
        flow = InstalledAppFlow.from_client_secrets_file(
            'your_client_secret_file.json', SCOPES)
        creds = flow.run_local_server(port=0)

        # Save the credentials to token.json
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

        # Save the client secrets to client_secrets.json
        with open(CLIENT_SECRETS_FILE, 'w') as client_secrets_file:
            json.dump(flow.client_config, client_secrets_file)

    else:
        # If client_secrets.json exists, load the credentials from token.json
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    return creds

# def initiate_oauth_flow():
#     """Initiates the OAuth flow to obtain credentials and saves them to client_secrets.json."""
#     if not os.path.exists(CLIENT_SECRETS_FILE):
#         # If client_secrets.json does not exist, initiate OAuth flow to create it
#         flow = InstalledAppFlow.from_client_secrets_file(
#             'your_client_secret_file.json', SCOPES)
#         creds = flow.run_local_server(port=0)

#         # Save the credentials to token.json
#         with open('token.json', 'w') as token:
#             token.write(creds.to_json())

#         # Wrap client config with "installed" key
#         client_config_wrapped = {"installed": flow.client_config}

#         # Save the client secrets to client_secrets.json with "installed" key
#         with open(CLIENT_SECRETS_FILE, 'w') as client_secrets_file:
#             json.dump(client_config_wrapped, client_secrets_file)

#     else:
#         # If client_secrets.json exists, load the credentials from token.json
#         creds = Credentials.from_authorized_user_file('token.json', SCOPES)

#     return creds

def analyze_emails():
    """Analyzes the user's latest 1000 emails and tracks sender statistics."""
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    try:

        service = build('gmail', 'v1', credentials=creds)

        sender_stats = {}

        results = service.users().messages().list(
            userId='me', labelIds=['INBOX'], q='', maxResults=1000).execute()
        messages = results.get('messages', [])

        unsubscribed_senders = load_unsubscribed_senders()

        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            email_data = msg['payload']['headers']

            sender_email = None
            for header in email_data:
                if header['name'] == 'From':
                    sender_email = header['value']
                    break

            if sender_email:
                if sender_email in unsubscribed_senders:
                    unsubscribe_timestamp = unsubscribed_senders[sender_email]
                    latest_email_timestamp = int(msg['internalDate']) / 1000
                    if latest_email_timestamp > unsubscribe_timestamp:
                        unsubscribed_senders.pop(sender_email)

                unsubscribe_links = extract_unsubscribe_link(email_data)
                if unsubscribe_links:
                    if sender_email not in sender_stats:
                        sender_stats[sender_email] = {'total_emails': 0, 'unread_emails': 0, 'unsubscribe_links': unsubscribe_links}

                    sender_stats[sender_email]['total_emails'] += 1

                    if 'UNREAD' in msg['labelIds']:
                        sender_stats[sender_email]['unread_emails'] += 1

        # Filter senders without unsubscribe links
        sender_stats_filtered = {sender: stats for sender, stats in sender_stats.items() if stats.get('unsubscribe_links')}

        # Check if sender has been unsubscribed previously
        sender_stats_filtered = {sender: stats for sender, stats in sender_stats_filtered.items() if sender not in unsubscribed_senders}

        # Sort senders by number of unread emails
        sender_stats_sorted = sorted(sender_stats_filtered.items(), key=lambda x: x[1]['unread_emails'], reverse=True)

        return sender_stats_sorted

    except Exception as error:
        print(f'An error occurred: {error}')
        return []

def load_unsubscribed_senders():
    """Loads the list of senders from which the user has unsubscribed along with their timestamps."""
    unsubscribed_senders = {}
    if os.path.exists(UNSUBSCRIBE_FILE):
        with open(UNSUBSCRIBE_FILE, 'r') as file:
            for line in file:
                sender, timestamp = line.strip().split(',')
                unsubscribed_senders[sender] = int(timestamp)
    return unsubscribed_senders

def save_unsubscribed_sender(sender):
    """Saves the unsubscribed sender along with the current timestamp to the file."""
    timestamp = int(datetime.now().timestamp())
    with open(UNSUBSCRIBE_FILE, 'a') as file:
        file.write(f"{sender},{timestamp}\n")

def open_unsubscribe_link(sender, link, button):
    """Opens the unsubscribe link and saves the sender to the list of unsubscribed senders."""
    if link.startswith("http://") or link.startswith("https://"):
        webbrowser.open_new(link)
        save_unsubscribed_sender(sender)
        button.config(state=tk.DISABLED)
    else:
        messagebox.showinfo("Invalid Link", "The unsubscribe link is not a valid web link.")

def display_sender_stats():
    """Displays sender statistics with unsubscribe links."""
    sender_stats = analyze_emails()

    root = tk.Tk()
    root.title("Sender Statistics")

    canvas = tk.Canvas(root)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor=tk.NW)

    frame.bind("<Configure>", lambda event, canvas=canvas: canvas.configure(scrollregion=canvas.bbox("all")))

    for idx, (sender, stats) in enumerate(sender_stats):
        label_sender = ttk.Label(frame, text=f"Sender: {sender}")
        label_sender.grid(row=idx, column=0, sticky="w")

        label_total_emails = ttk.Label(frame, text=f"Total Emails: {stats['total_emails']}")
        label_total_emails.grid(row=idx, column=1, sticky="w")

        label_unread_emails = ttk.Label(frame, text=f"Unread Emails: {stats.get('unread_emails', 0)}")
        label_unread_emails.grid(row=idx, column=2, sticky="w")

        if stats.get('unsubscribe_links'):
            btn_unsubscribe = ttk.Button(frame, text="Unsubscribe")
            btn_unsubscribe.grid(row=idx, column=3, sticky="w")
            btn_unsubscribe.config(command=lambda s=sender, l=stats['unsubscribe_links'][0], b=btn_unsubscribe: open_unsubscribe_link(s, l, b))


    canvas.configure(yscrollcommand=scrollbar.set)

    root.mainloop()

if __name__ == "__main__":
    display_sender_stats()
