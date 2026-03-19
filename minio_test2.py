from minio import Minio
from minio.error import S3Error

class S3FileManager:
    def __init__(self, config):
        """
        Initialize the MinIO client using the provided configuration.
        """
        self.client = Minio(
            endpoint=config["endpoint"],
            access_key=config["access_key"],
            secret_key=config["secret_key"],
            secure=config["secure"]
        )

    def get_specific_file_details(self, bucket_name, file_name):
        """
        Check if a specific file exists in a bucket and list its details in MB.
        """
        try:
            # stat_object fetches the metadata of the specific object
            result = self.client.stat_object(bucket_name, file_name)
            
            # Calculate size in MB
            size_mb = result.size / (1024 * 1024)
            
            print(f"✅ File Found: {result.object_name}")
            print(f"   - Bucket: {result.bucket_name}")
            print(f"   - Size: {size_mb:.2f} MB")  # Updated to MB
            print(f"   - Last Modified: {result.last_modified}")
            print(f"   - Content Type: {result.content_type}")
            
            return result

        except S3Error as exc:
            if exc.code == "NoSuchKey":
                print(f"❌ Error: The file '{file_name}' does not exist in bucket '{bucket_name}'.")
            elif exc.code == "NoSuchBucket":
                print(f"❌ Error: The bucket '{bucket_name}' does not exist.")
            else:
                print(f"❌ An error occurred: {exc}")
            return None

    def delete_specific_file(self, bucket_name, file_name):
        """
        Delete a specific file from the bucket.
        """
        try:
            # First, check if the file actually exists to provide better user feedback
            # (Because S3 delete operations usually return 'success' even if the file wasn't there)
            self.client.stat_object(bucket_name, file_name)
            
            # Remove the object
            self.client.remove_object(bucket_name, file_name)
            print(f"🗑️ Success: The file '{file_name}' has been deleted from '{bucket_name}'.")
            return True
            
        except S3Error as exc:
            if exc.code == "NoSuchKey":
                print(f"❌ Cannot delete: The file '{file_name}' does not exist in bucket '{bucket_name}'.")
            else:
                print(f"❌ An error occurred while trying to delete: {exc}")
            return False

# --- Example Usage ---
if __name__ == "__main__":
    config = {
        "endpoint": "minio.example.com:9000",
        "access_key": "access_key",
        "secret_key": "secret_key",
        "secure": False
    }

    # Initialize the manager
    s3_manager = S3FileManager(config)

    # Define your targets
    TARGET_BUCKET = "my-test-bucket"
    TARGET_FILE = "folder/my-specific-file.txt"

    print("--- Checking File ---")
    file_exists = s3_manager.get_specific_file_details(TARGET_BUCKET, TARGET_FILE)

    # Uncomment the below lines if you want to trigger the deletion
    """
    if file_exists:
        print("\n--- Deleting File ---")
        s3_manager.delete_specific_file(TARGET_BUCKET, TARGET_FILE)
    """
