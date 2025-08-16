import os
import pickle
import schedule
import time
import logging
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime

# Configure logging to a file
logging.basicConfig(
    filename=os.path.expanduser('~/gmail_check.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Scopes for read-only access to Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    """Authenticate and return Gmail API service."""
    creds = None
    token_path = os.path.expanduser('~/token.pickle')
    creds_path = os.path.expanduser('~/credentials.json')
    
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        try:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(creds_path):
                    logging.error("credentials.json not found")
                    raise FileNotFoundError("credentials.json not found")
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                creds = flow.run_local_server(port=0)
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
            logging.info("Authentication successful")
        except Exception as e:
            logging.error(f"Authentication failed: {e}")
            raise
    
    return build('gmail', 'v1', credentials=creds)

def get_latest_emails(service, max_results=5):
    """Fetch and log the latest emails from the inbox."""
    try:
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=max_results).execute()
        messages = results.get('messages', [])
        
        if not messages:
            logging.info("No new emails found")
            print(f"{datetime.now()}: No new emails found")
            return
        
        logging.info(f"Found {len(messages)} new emails")
        print(f"{datetime.now()}: Latest {len(messages)} emails:")
        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
            headers = msg_data['payload']['headers']
            
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            from_addr = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
            
            log_message = f"From: {from_addr}, Subject: {subject}, Date: {date}"
            print(f"\nFrom: {from_addr}\nSubject: {subject}\nDate: {date}\n{'-' * 50}")
            logging.info(log_message)
            
    except Exception as e:
        logging.error(f"Error fetching emails: {e}")
        print(f"{datetime.now()}: Error fetching emails: {e}")

def check_emails_job():
    """Job to check emails."""
    try:
        service = authenticate_gmail()
        get_latest_emails(service, max_results=5)
    except Exception as e:
        logging.error(f"Failed to run email check: {e}")
        print(f"{datetime.now()}: Failed to run email check: {e}")

def main():
    # Schedule the job every 3 hours
    schedule.every(3).hours.do(check_emails_job)
    logging.info("Scheduled email check every 3 hours")
    print(f"{datetime.now()}: Scheduled email check every 3 hours")
    
    # Run the first check immediately
    check_emails_job()
    
    # Keep the script running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logging.info("Script stopped by user")
        print(f"{datetime.now()}: Script stopped by user")
    except Exception as e:
        logging.error(f"Script error: {e}")
        print(f"{datetime.now()}: Script error: {e}")

if __name__ == '__main__':
    main()
