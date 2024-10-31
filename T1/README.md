
# TMail v0.1.2
A powerful command line-based email client designed for efficient email management directly from your terminal. This client enables users to view emails, mark them as read or unread, report spam, delete emails, and perform batch operations. Additionally, it offers an email summarization feature using Gemini 1.5 Flash for quick insights into your inbox.

## Features
- **View Emails**: Display your emails in a clean and organized format.
- **Mark as Read/Unread**: Easily toggle the read status of individual or multiple emails.
- **Report Spam**: Quickly mark emails as spam to filter unwanted messages.
- **Delete Emails**: Remove unwanted emails individually or in batch.
- **Batch Operations**: Execute actions like marking as read/unread, reporting spam, or deleting multiple emails at once.
- **Email Summarization**: Leverage Gemini 1.5 Flash to generate concise summaries of email texts for quick understanding.
- **Download All attachments**: Download all the attachments present in an email.
- **Search for emails**: Search for emails by date,read/unread status,attachments and many more options.

## Installation
1. Clone the repository :
```
git clone https://github.com/gmbcode/R3T_Project.git
cd T1
```
2. Install the dependencies (preferably in a virtual environment)
`pip install -r requirements.txt`

3. Go to Google Cloud Console and create a new project
4. Enable Gmail API and go to OAuth Consent Screen and set up your app name and other parameters as required
5. In the required scopes add the scope `https://mail.google.com/`
6. Download the credentials and store them in a file named `credentials.json` in the T1 directory
7. Go to Google AI Studio and get Gemini API key
8. Store your Gemini API Key in an `.env` file stored in the T1 directory in the following format
``` 
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```
## Usage
 Run `main.py` without arguments and sign in to your email.
 > [!NOTE]
>Make sure your email is added as one of the test emails in your OAuth Consent screen before logging into the app
## License
[GNU LGPLv3](https://choosealicense.com/licenses/lgpl-3.0/)
