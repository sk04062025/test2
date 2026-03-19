# s3_manager.py
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
        Check if a specific file exists in a bucket and list its details.
        """
        try:
            # stat_object fetches the metadata of the specific object
            result = self.client.stat_object(bucket_name, file_name)
            
            print(f"✅ File Found: {result.object_name}")
            print(f"   - Bucket: {result.bucket_name}")
            print(f"   - Size: {result.size / 1024:.2f} KB")
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

    # Fetch file details
    s3_manager.get_specific_file_details(TARGET_BUCKET, TARGET_FILE)
