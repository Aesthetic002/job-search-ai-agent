"""
Configuration for Firebase (Firestore) and Azure Blob Storage
"""
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore, storage
from azure.storage.blob import BlobServiceClient

load_dotenv()

# ==================== FIREBASE CONFIGURATION ====================

def init_firebase():
    """Initialize Firebase Admin SDK."""
    try:
        # Check if already initialized
        firebase_admin.get_app()
        print("✅ Firebase already initialized")
    except ValueError:
        # Initialize Firebase
        cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")

        if not os.path.exists(cred_path):
            raise FileNotFoundError(
                f"Firebase credentials file not found at: {cred_path}\n"
                f"Please create the file or update FIREBASE_CREDENTIALS_PATH in .env"
            )

        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {
            'storageBucket': os.getenv("FIREBASE_STORAGE_BUCKET")
        })
        print("✅ Firebase initialized successfully")


def get_firestore_client():
    """Get Firestore database client."""
    init_firebase()
    return firestore.client()


def get_firebase_storage_bucket():
    """Get Firebase Storage bucket (optional - we're using Azure)."""
    init_firebase()
    return storage.bucket()


# ==================== AZURE BLOB STORAGE CONFIGURATION ====================

def get_azure_blob_service_client():
    """Get Azure Blob Storage service client."""
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    if not connection_string:
        raise ValueError(
            "AZURE_STORAGE_CONNECTION_STRING not found in environment variables.\n"
            "Please add it to your .env file."
        )

    return BlobServiceClient.from_connection_string(connection_string)


def get_azure_container_client(container_name: str = None):
    """Get Azure Blob container client."""
    if container_name is None:
        container_name = os.getenv("AZURE_STORAGE_CONTAINER", "resumes")

    blob_service_client = get_azure_blob_service_client()

    # Create container if it doesn't exist
    try:
        container_client = blob_service_client.get_container_client(container_name)
        if not container_client.exists():
            container_client.create_container()
            print(f"✅ Created Azure container: {container_name}")
    except Exception as e:
        print(f"⚠️  Container creation issue: {e}")

    return blob_service_client.get_container_client(container_name)


# ==================== HELPER FUNCTIONS ====================

def upload_file_to_azure(
    file_data: bytes,
    blob_name: str,
    container_name: str = None,
    content_type: str = "application/pdf"
) -> str:
    """
    Upload a file to Azure Blob Storage.

    Args:
        file_data: File content as bytes
        blob_name: Name/path of the blob (e.g., "users/123/resume.pdf")
        container_name: Container name (default from env)
        content_type: MIME type of the file

    Returns:
        URL of the uploaded blob
    """
    container_client = get_azure_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)

    # Upload with metadata
    blob_client.upload_blob(
        file_data,
        overwrite=True,
        content_settings={
            'content_type': content_type
        }
    )

    return blob_client.url


def download_file_from_azure(
    blob_name: str,
    container_name: str = None
) -> bytes:
    """
    Download a file from Azure Blob Storage.

    Args:
        blob_name: Name/path of the blob
        container_name: Container name (default from env)

    Returns:
        File content as bytes
    """
    container_client = get_azure_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)

    return blob_client.download_blob().readall()


def delete_file_from_azure(
    blob_name: str,
    container_name: str = None
) -> bool:
    """
    Delete a file from Azure Blob Storage.

    Args:
        blob_name: Name/path of the blob
        container_name: Container name (default from env)

    Returns:
        True if deleted successfully
    """
    try:
        container_client = get_azure_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.delete_blob()
        return True
    except Exception as e:
        print(f"Error deleting blob: {e}")
        return False


def get_blob_url(
    blob_name: str,
    container_name: str = None,
    expiry_hours: int = 24
) -> str:
    """
    Get a temporary signed URL for a blob.

    Args:
        blob_name: Name/path of the blob
        container_name: Container name (default from env)
        expiry_hours: How long the URL should be valid (hours)

    Returns:
        Signed URL with SAS token
    """
    from datetime import datetime, timedelta
    from azure.storage.blob import generate_blob_sas, BlobSasPermissions

    container_client = get_azure_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)

    # Generate SAS token
    sas_token = generate_blob_sas(
        account_name=blob_client.account_name,
        container_name=container_client.container_name,
        blob_name=blob_name,
        account_key=os.getenv("AZURE_STORAGE_ACCOUNT_KEY"),
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=expiry_hours)
    )

    return f"{blob_client.url}?{sas_token}"


# ==================== INITIALIZATION TEST ====================

if __name__ == "__main__":
    print("\n" + "="*50)
    print("Testing Configuration")
    print("="*50 + "\n")

    # Test Firebase
    try:
        print("Testing Firebase...")
        init_firebase()
        db = get_firestore_client()
        print("✅ Firestore connection successful")
    except Exception as e:
        print(f"❌ Firebase error: {e}")

    # Test Azure
    try:
        print("\nTesting Azure Blob Storage...")
        container = get_azure_container_client()
        print(f"✅ Azure Blob Storage connection successful")
        print(f"   Container: {container.container_name}")
    except Exception as e:
        print(f"❌ Azure error: {e}")

    print("\n" + "="*50)
