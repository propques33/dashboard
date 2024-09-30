import os
import json
import base64
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db

# Load the .env file
load_dotenv()

# Decode the base64 encoded Firebase service account JSON and initialize Firebase Admin SDK
def initialize_firebase():
    try:
        firebase_service_account_base64 = os.getenv('FIREBASE_SERVICE_ACCOUNT_BASE64')
        if not firebase_service_account_base64:
            raise ValueError("FIREBASE_SERVICE_ACCOUNT_BASE64 environment variable is not set")

        firebase_service_account_json = json.loads(base64.b64decode(firebase_service_account_base64).decode('utf-8'))
        cred = credentials.Certificate(firebase_service_account_json)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://propclean-default-rtdb.firebaseio.com/'
        })
    except Exception as e:
        print(f"Failed to initialize Firebase: {e}")
        exit(1)

def fetch_data():
    # Fetch data from the specific 'backup' node
    try:
        ref = db.reference('backup')  # Reference the 'backup' node
        data = ref.get()
        if data:
            return data
        else:
            return {}
    except Exception as e:
        print(f"Failed to fetch data from 'backup' node: {e}")
        return {}

# Initialize Firebase and fetch data
initialize_firebase()
data = fetch_data()
