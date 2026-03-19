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
            file_names = [file_names]

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
            file_names = [file_names]

        print(f"\n--- Deleting {len(file_names)} File(s) ---")
        
        # Prepare list of objects to delete
        delete_object_list = [DeleteObject(file) for file in file_names]
        
        # remove_objects returns a generator with any deletion errors
        errors = self.client.remove_objects(bucket_name, delete_object_list)
        
        error_count = 0
        for error in errors:
            print(f"❌ Error deleting '{error.name}': {error.message}")
            error_count += 1
            
        if error_count == 0:
            print(f"🗑️ Success: All {len(file_names)} file(s) requested for deletion were processed.")

    def delete_folders(self, bucket_name, folder_names):
        """
        Delete a list of folders (prefixes) and all their contents from the bucket.
        """
        if not isinstance(folder_names, list):
            folder_names = [folder_names]

        print(f"\n--- Deleting {len(folder_names)} Folder(s) ---")
        
        delete_object_list =[]
        unique_keys = set() # To prevent duplicates if overlapping folders are passed

        for folder_name in folder_names:
            # Ensure the folder name ends with a '/' to prevent accidentally deleting 
            # files that just happen to share the same starting characters.
            if not folder_name.endswith('/'):
                folder_name += '/'

            try:
                # List all objects inside this "folder" (prefix)
                objects_to_delete = self.client.list_objects(bucket_name, prefix=folder_name, recursive=True)
                
                folder_obj_count = 0
                for obj in objects_to_delete:
                    # Only add to deletion list if we haven't already added it
                    if obj.object_name not in unique_keys:
                        unique_keys.add(obj.object_name)
                        delete_object_list.append(DeleteObject(obj.object_name))
                        folder_obj_count += 1
                
                print(f"📁 Identified {folder_obj_count} file(s) inside folder '{folder_name}'.")
                
            except S3Error as exc:
                print(f"❌ Error accessing folder '{folder_name}': {exc}")

        if not delete_object_list:
            print("⚠️ No files found inside any of the specified folders.")
            return False

        # Execute bulk deletion for all collected files across all folders
        errors = self.client.remove_objects(bucket_name, delete_object_list)
        
        error_count = 0
        for error in errors:
            print(f"❌ Error deleting '{error.name}': {error.message}")
            error_count += 1
            
        if error_count == 0:
            print(f"🗑️ Success: All {len(delete_object_list)} file(s) across {len(folder_names)} folder(s) have been deleted.")
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

    # 1. Provide a list of folders you want to completely delete
    folders_to_delete =[
        "logs/2023/",
        "temp_data",         # Script will automatically append '/' to this
        "archives/old_files/"
    ]

    # Execute the bulk folder deletion
    s3_manager.delete_folders(TARGET_BUCKET, folders_to_delete)
