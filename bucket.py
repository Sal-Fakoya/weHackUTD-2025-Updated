import boto3
import logging
import os
import pandas as pd
import pathlib
from glob import glob


# Create Global Variables
file = "rootkey.csv"
aws_region_name = "us-east-2"
BUCKET_NAME = "website-sample-bucket"
DOWNLOADS_DIR = "downloads"


# Connect to S3 Bucket: To connect to S3 Bucket, call createSession(file=) 
"""
createSession: is a function that creates an S3 session. 
    parameters: file - is the .csv file containing the access key id 
                        and secret access key directly downloaded from AWS S3.
"""

def createSession(file, aws_region_name = "us-east-2"):
    # Read AWS credentials from CSV file
    key_file = pd.read_csv(file)
    access_key_id = key_file.loc[0, "Access key ID"]
    secret_access_key = key_file.loc[0, "Secret access key"]
    
    # Create a session with the provided credentials
    session = boto3.Session(
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key,
    region_name=aws_region_name
    )
    
    return session

# Initialize session
session = createSession(file = file)


# List buckets 
def list_buckets(prefix=None): 
    # Create S3 resource and client using the session 
    s3_resource = session.resource('s3') 
    s3_client = session.client('s3') 
    
    try: 
        buckets = list(s3_resource.buckets.all()) 
        
        if prefix: 
            # Sort buckets with those starting with the prefix first 
            buckets_sorted = sorted(buckets, key=lambda bucket: (not bucket.name.lower().startswith(prefix.lower()), bucket.name)) 
        
        else: 
            buckets_sorted = buckets 
            
        for bucket in buckets_sorted: 
            bucket_name = bucket.name 
            # Get bucket location 
            response = s3_client.get_bucket_location(Bucket=bucket_name) 
            bucket_location = response["LocationConstraint"] 
            print(f"Bucket: {bucket_name}, Location: {bucket_location}") 
                
    except Exception as e:
        print("Error Listing Buckets")

    
# Create s3 Bucket:
def createBucket(bucket_name, aws_region_name = "us-east-2"):
    s3_resource = session.resource("s3")
    s3_client = session.client("s3")
    
    print(f"\n***Creating New Bucket: {bucket_name}")
    
    # Get s3 resource bucket
    bucket = s3_resource.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration=
        {
            'LocationConstraint': aws_region_name
        }
    )
    
    bucket.wait_until_exists()
    
    print(f"\n****Bucket Created. List Buckets:\n")
    list_buckets()
     
    
# Deleting s3 Bucket
def deleteBucket(bucket_name):
    s3_resource = session.resource("s3")
    
    # Get s3 resource bucket
    bucket = s3_resource.Bucket(bucket_name)
    
    print(f"****Deleting Bucket: {bucket}...")
    # Delete all versions in the bucket 
    
    for version in bucket.object_versions.all(): 
        version.delete()
        
    # Call the delete()
    bucket.delete()
    
    bucket.wait_until_not_exists()
    print("****\nBucket Deleted. Remaining Buckets: \n")
    list_buckets()
    

# Bucket Versioning Support for AWS S3 Buckets:
def enable_Bucket_Versioning_Support(bucket_name):
    
    s3_resource = session.resource("s3")
    bucket_versioning = s3_resource.BucketVersioning(bucket_name) # create the bucket_versioning object
    
    bucket_versioning.enable() # enable bucket verisoning
    
    print(f"\n****Bucket versioning support: {bucket_versioning.status}")


# Uploading files and folders to S3 Bucket
def uploadFiles(bucket_name, *file_paths):
    try:
        s3_resource = session.resource("s3")

        for path in file_paths:
            if os.path.isdir(path):
                root_path = path  # local folder for upload

                my_bucket = s3_resource.Bucket(bucket_name)
                
                for root, subdirs, files in os.walk(root_path):
                    folder_name = os.path.basename(root_path)
                    relative_root = os.path.relpath(root, root_path)
                    s3_folder_path = os.path.join(folder_name, relative_root).replace("\\", "/")
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        s3_key = os.path.join(s3_folder_path, file).replace("\\", "/")
                        my_bucket.upload_file(file_path, s3_key)
                        print(f"Successfully uploaded {file_path} to {bucket_name}/{s3_key}")
            else:
                # Upload a single file
                file_name = os.path.basename(path)
                s3_resource.Bucket(bucket_name).upload_file(path, file_name)
                print(f"Successfully uploaded {path} to {bucket_name}/{file_name}")

    except Exception as e:
        print(f"Failed to upload {path}: {e}")


# Write DataFrame to S3 Bucket:
def writeDataframe_to_S3(df, bucket_name):
    try:
        df = pd.DataFrame.to_csv(df)
        uploadFiles(bucket_name, df)
    except Exception as e:
        print("Failed to upload DataFrame")


# List and filter objects from s3 buckets:
def listAndFilter_Bucket(bucket_name, prefix = None):
    object_versions = getS3_objectVersions(bucket_name, prefix)
    for object in object_versions:
        print(f"-- {object.key}")


# Get s3 object versions
def getS3_objectVersions(bucket_name, prefix=None):
    s3_resource = session.resource("s3")
    bucket = s3_resource.Bucket(bucket_name)
    
    if not prefix:
        prefix = ""
        
    objects_versions = bucket.objects.filter(Prefix=prefix)
        
    return objects_versions

# Download S3 objects to local machine
def downloadS3_Objects(bucket_name, prefix=None):
    try:
        object_versions = getS3_objectVersions(bucket_name=bucket_name, prefix=prefix)
        for obj_version in object_versions:
            obj = obj_version.Object()
            obj_key = obj.key  # stores the files in the s3 bucket
            
            # s3-subpath is a list of paths
            s3_subpath = obj_key.split("/")[:-1]  # take the rest of the path's list except the file name.
            s3_file_name = obj_key.split("/")[-1]  # Get the file name
            
            local_subfolder = os.path.join(DOWNLOADS_DIR, *s3_subpath)  # Get the files from the s3 subpath.
            
            if not os.path.exists(local_subfolder):
                os.makedirs(local_subfolder)  # Create the local subfolder if it does not exist in the local machine.
            
            obj.download_file(os.path.join(local_subfolder, s3_file_name))  # downloads the files to the local_subfolder
            print(f"Successfully downloaded {obj_key} to {local_subfolder}/{s3_file_name}")
    except Exception as e:
        print(f"Failed to download objects: {e}")

# Delete Objects and their versios from S3 Buckets
def deleteObjects(bucket_name, prefix = None):
    s3_resource = session.resource("s3")
    bucket = s3_resource.Bucket(bucket_name)
    
    # To delete the object...
    if prefix:
        bucket.objects.filter(Prefix = prefix).delete()
    else:
        bucket.objects.delete()
        
# Delete Object Version
def deleteObjects_Versions(bucket_name, prefix = None):
    s3_resource = session.resource("s3")
    bucket = s3_resource.Bucket(bucket_name)
    
    # To delete the object versions...
    if prefix:
        bucket.object_versions.filter(Prefix = prefix).delete()
    else:
        bucket.object_versions.delete()

# Empty S3 Bucket, i.e delete objects in s3 bucket
def emptyS3Bucket(bucket_name, prefix = None):
    deleteObjects(bucket_name, prefix)
    deleteObjects_Versions(bucket_name, prefix)



# Copying and Moving Objects Within the AWS S3 Bucket
def copyingAndMovingObjects(bucket_name, source_object, destination_object):
    # Create S3 resource and client using the session
    s3_resource = session.resource('s3')

    try:
        s3_resource = session.resource("s3")
        bucket = s3_resource.Bucket(bucket_name)
        
        # Copy object to destination
        copy_source = {'Bucket': bucket_name, 'Key': source_object}
        s3_resource.Object(bucket_name, destination_object).copy(copy_source)
        print(f"Successfully copied {source_object} to {destination_object}")

        # Optionally, delete the original object if you want to move it
        bucket.Object(source_object).delete()
        print(f"Successfully moved {source_object} to {destination_object}")

    except Exception as e:
        print(f"Failed to copy and move {source_object}: {e}")


# Generating pre-signed URLs for Objects in S3 Buckets:
def generatePreSignedURL(bucket_name, object_key):
    s3_client = session.client("s3") # allows us to generate pre-signed URLs
    
    url = s3_client.generate_presigned_url(
        ClientMethod = "get_object", 
        Params = {"Bucket": bucket_name, "Key": object_key}, 
        ExpiresIn=3600
    ) # This will generate the URL
    # To download from the URL in powershell terminal, run:
    """
    curl -o "object_key_or_file_name" "your_link"

    """
    
    print(f"Download URL: {url}")


if __name__ == "__main__": 
    listAndFilter_Bucket(bucket_name=BUCKET_NAME)
    # Example usage: 
    copyingAndMovingObjects(bucket_name=BUCKET_NAME, 
                            source_object="Degree_Plan_and_Flowchart/./Data Science.BS.24flowchart.pdf", 
                            destination_object="new_data.csv")
    listAndFilter_Bucket(bucket_name=BUCKET_NAME)
    
    generatePreSignedURL(bucket_name=BUCKET_NAME, object_key="Data Science.BS.24flowchart.pdf")
    
    
    
    


