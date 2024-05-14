import firebase_admin
from firebase_admin import credentials, firestore

# Path to your service account key JSON file
service_account_key_path = "agrisenzebigdata-service-account-key.json"

# Initialize Firebase with service account credentials
cred = credentials.Certificate(service_account_key_path)
firebase_admin.initialize_app(cred, options={
    "databaseURL": "https://agrisenzebigdata.firebaseio.com"
})
# Get a reference to the Firestore database
db = firestore.client()


