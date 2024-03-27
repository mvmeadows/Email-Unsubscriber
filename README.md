## Overview
This Desktop Application is used to analyze your personal email and provide unsubscribe links to all 
those pesky companies you gave your email to who knows when! 

The code is currently set to analyze your latest 1000 emails and only provide email senders who have an unsubscribe link. 

The application returns a view of Sender, Total Emails, Total Unread Emails, and an Unsubscribe Button. This is 
filtered to have the most unread emails at the top. 

The Unsubscribe Button will open up a brower where you can unsubscribe from the email sender. If a valid
web link is not available, a pop up will show informing you that there is no valid web link.

When you click "Unsubscribe", a file called "unsubscribed_senders.txt" is created locally for all senders 
you unsubscribed from with a timestamp so that when emails are analyzed again, there are no repeat senders, unless
the email was recieved after you already unsubscribed. 

## Set Up
Currently, in order to set up this application, you will need to create a client_secrets.json file and store it in the 
same location as main.exe. To create client_secrets.json, follow the steps below:

1. Go to the Google Cloud Console: https://console.cloud.google.com/
2. Select your project or create a new one.
3. Navigate to the "APIs & Services" > "Credentials" page.
4. Click on "Create credentials" and select "OAuth client ID."
5. Choose "Desktop app" as the application type.
6. Fill in other required details (such as the name) and click "Create."
7. Download the credentials file (JSON) and rename it to client_secrets.json.
8. Save the file in the folder dist/main

## Enabling Gmail API
The Gmail API needs to be enabled within the Google Cloud Console. To do so follow these steps: 
1. Go to the Google Cloud Console: https://console.cloud.google.com/
2. Select your project.
3. Navigate to the "APIs & Services" > "Enabled APIs & services" page.
4. Click "ENABLE APIS AND SERICES"
5. Search for "Gmail API" and select it
6. Click "Enable"

## Create Test Users
Test users need to be created with the email of the email you want to analyze.

1. Go to the Google Cloud Console: https://console.cloud.google.com/
2. Select your project.
3. Navigate to the "APIs & Services" > "OAuth consent screen" page.
4. Click "ADD USERS" 
5. Enter the email you want to analyze and click "Save"

## Run
Run main.exe, and a screen will pop up that says "Analyze Emails" 

Click "Analyze Emails" and you will be taken to a new browser to sign into your email

You will be prompted of an unverfied application, click continue

Allow access to atleast View your email messages and settings

This will create a token.json file to access email data 

After the application has run, a new screen will pop up to allow you to unsubscribe from emails

## Privacy Notice
For this application, no email data is stored in any database or locally. Data is only analyzed to return a total amount
of emails per sender, total amount of unread and read emails, and an unsubscribe link