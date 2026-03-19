from minio import Minio
from minio.error import S3Error
from minio.deleteobjects import DeleteObject

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

    def get_files_details(self, bucket_name, file_names):
        """
        Check existence and list details in MB for a list of specific files.
        """
        if not isinstance(file_names, list):
            file_names =[file_names] # Convert to list if a single string is passed

        print(f"\n--- Checking {len(file_names)} File(s) ---")
        for file_name in file_names:
            try:
                result = self.client.stat_object(bucket_name, file_name)
                size_mb = result.size / (1024 * 1024)
                print(f"✅ Found: '{result.object_name}' | Size: {size_mb:.4f} MB | Modified: {result.last_modified}")
            
            except S3Error as exc:
                if exc.code == "NoSuchKey":
                    print(f"❌ Not Found: The file '{file_name}' does not exist.")
                else:
                    print(f"❌ Error checking '{file_name}': {exc}")

    def delete_files(self, bucket_name, file_names):
        """
        Delete a list of specific files using bulk deletion.
        """
        if not isinstance(file_names, list):
            file_names =[file_names]

        print(f"\n--- Deleting {len(file_names)} File(s) ---")
        
        # Prepare list of objects to delete
        delete_object_list =[DeleteObject(file) for file in file_names]
        
        # remove_objects returns a generator with any deletion errors
        errors = self.client.remove_objects(bucket_name, delete_object_list)
        
        error_count = 0
        for error in errors:
            print(f"❌ Error deleting '{error.name}': {error.message}")
            error_count += 1
            
        if error_count == 0:
            print(f"🗑️ Success: All {len(file_names)} file(s) requested for deletion were processed.")

    def delete_folder(self, bucket_name, folder_name):
        """
        Delete an entire folder (prefix) and all its contents from the bucket.
        """
        print(f"\n--- Deleting Folder: '{folder_name}' ---")
        
        # Ensure the folder name ends with a '/' to prevent accidentally deleting 
        # files that just happen to share the same starting characters.
        if not folder_name.endswith('/'):
            folder_name += '/'

        # List all objects inside this "folder" (prefix)
        objects_to_delete = self.client.list_objects(bucket_name, prefix=folder_name, recursive=True)
        
        # Convert to MinIO DeleteObjects
        delete_object_list =[DeleteObject(obj.object_name) for obj in objects_to_delete]

        if not delete_object_list:
            print(f"⚠️ No files found inside folder '{folder_name}'.")
            return False

        # Execute bulk deletion
        errors = self.client.remove_objects(bucket_name, delete_object_list)
        
        error_count = 0
        for error in errors:
            print(f"❌ Error deleting '{error.name}': {error.message}")
            error_count += 1
            
        if error_count == 0:
            print(f"🗑️ Success: Entire folder '{folder_name}' ({len(delete_object_list)} files) has been deleted.")
            return True
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
    TARGET_BUCKET = "my-test-bucket"

    # 1. Pass a list of files to get details
    files_to_check =[
        "folder/my-specific-file1.txt",
        "folder/my-specific-file2.txt",
        "folder/does-not-exist.jpg"
    ]
    s3_manager.get_files_details(TARGET_BUCKET, files_to_check)

    # 2. Pass a list of files to delete
    # s3_manager.delete_files(TARGET_BUCKET, files_to_check)

    # 3. Pass a folder name to delete the whole folder and its contents
    # s3_manager.delete_folder(TARGET_BUCKET, "folder")
