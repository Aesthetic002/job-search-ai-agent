"""
Simple test script for Firebase and Azure configuration (Windows compatible)
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*60)
print("Testing Firebase and Azure Configuration")
print("="*60 + "\n")

# Test 1: Firebase
print("[1/3] Testing Firebase...")
try:
    import firebase_admin
    from firebase_admin import credentials, firestore

    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")

    if not os.path.exists(cred_path):
        print(f"[FAIL] Firebase credentials file not found at: {cred_path}")
        sys.exit(1)

    # Initialize Firebase
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {
        'storageBucket': os.getenv("FIREBASE_STORAGE_BUCKET")
    })

    # Get Firestore client
    db = firestore.client()

    print("[PASS] Firebase initialized successfully")
    print(f"       Project ID: {os.getenv('FIREBASE_PROJECT_ID')}")
    print(f"       Storage Bucket: {os.getenv('FIREBASE_STORAGE_BUCKET')}")

except Exception as e:
    print(f"[FAIL] Firebase error: {str(e)}")
    sys.exit(1)

# Test 2: Azure Blob Storage
print("\n[2/3] Testing Azure Blob Storage...")
try:
    from azure.storage.blob import BlobServiceClient

    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    if not connection_string:
        print("[FAIL] AZURE_STORAGE_CONNECTION_STRING not found in .env")
        sys.exit(1)

    # Create Blob Service Client
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Try to get container (create if not exists)
    container_name = os.getenv("AZURE_STORAGE_CONTAINER", "resumes")
    container_client = blob_service_client.get_container_client(container_name)

    if not container_client.exists():
        container_client.create_container()
        print(f"[INFO] Created container: {container_name}")

    print("[PASS] Azure Blob Storage connected successfully")
    print(f"       Account: {os.getenv('AZURE_STORAGE_ACCOUNT_NAME')}")
    print(f"       Container: {container_name}")

except Exception as e:
    print(f"[FAIL] Azure error: {str(e)}")
    sys.exit(1)

# Test 3: Write test document to Firestore
print("\n[3/3] Testing Firestore write/read...")
try:
    # Write test document
    test_ref = db.collection('_test').document('config_test')
    test_ref.set({
        'test': True,
        'message': 'Configuration test successful',
        'timestamp': firestore.SERVER_TIMESTAMP
    })

    # Read it back
    doc = test_ref.get()
    if doc.exists:
        print("[PASS] Firestore write/read successful")
        print(f"       Test document created")

        # Clean up
        test_ref.delete()
        print(f"       Test document deleted")
    else:
        print("[FAIL] Could not read test document")
        sys.exit(1)

except Exception as e:
    print(f"[FAIL] Firestore write/read error: {str(e)}")
    sys.exit(1)

print("\n" + "="*60)
print("ALL TESTS PASSED!")
print("="*60)
print("\nYour Firebase and Azure setup is working correctly.")
print("You can now run the auth and analytics services.\n")
