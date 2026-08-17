from google.cloud import storage

import purchase_order_schedule
import purchase_order_confirmation
import inbound_delivery
import invoice
import functions_framework
import os

# Bucket name in GCP
BUCKET_NAME = "supply-chain-raw-data-1"


def upload_output_folder_to_gcs(bucket_name, local_folder="output"):
  # Initialize the Google Cloud Storage client, which handles authentication automatically based on environment credentials
  storage_client = storage.Client()
  # Get the reference to the GCS bucket using the provided name
  bucket = storage_client.bucket(bucket_name)

  if not os.path.exists(local_folder):
    print(f"Folder {local_folder} tidak ditemukan!")
    return

  for file_name in os.listdir(local_folder):
    if file_name.endswith(".csv"):
      local_path = os.path.join(local_folder, file_name)
      # Define the path in GCS where the file will be uploaded
      blob_path = f"raw/{file_name}"

      # Create a blob (object) reference for the file within the bucket
      blob = bucket.blob(blob_path)
      # Upload the file from the local path to the defined GCS blob path with the correct content type
      blob.upload_from_filename(local_path, content_type="text/csv")
      print(f"[SUCCESS] Files {file_name} uploaded to gs://{bucket_name}/{blob_path}")

@functions_framework.http
def main(request):
    try:
       #run the pipeline
        purchase_order_schedule.run()
        purchase_order_confirmation.run()
        inbound_delivery.run()
        invoice.run()

        #upload into GCS bucket
        upload_output_folder_to_gcs(BUCKET_NAME)

        return (
            f"New data has been created and uploaded to gs://{BUCKET_NAME}/raw/",
            200,
        )

    except Exception as e:
        print(f"Pipeline Error: {str(e)}")
        return (f"Error: {str(e)}", 500)

if __name__ == "__main__":
    main(None)