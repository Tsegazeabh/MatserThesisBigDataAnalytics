# from fastapi import FastAPI, File, UploadFile, HTTPException
# from google.cloud import storage, dataproc
# from fastapi import APIRouter, HTTPException
# import os

# # Initialize GCS and Dataproc clients
# storage_client = storage.Client()
# dataproc_client = dataproc.ClusterControllerClient()

# # Replace these values with your GCS bucket name and Dataproc cluster name
# BUCKET_NAME = "agrisenzedb"
# CLUSTER_NAME = "cluster-0829"
# uploadData = APIRouter(
#     tags=["Weather Data APIs"]
# )
# @uploadData.post("/process_data/")
# async def process_data(file: UploadFile = File(...)):
#     # Save the uploaded file to a temporary location
#     file_path = f"/tmp/{file.filename}"
#     with open(file_path, "wb") as f:
#         f.write(await file.read())
    
#     try:
#         # Upload the file to GCS
#         bucket = storage_client.bucket(BUCKET_NAME)
#         blob = bucket.blob(file.filename)
#         blob.upload_from_filename(file_path)

#         # Submit a job to the Dataproc cluster
#         job_details = {
#             "placement": {"cluster_name": CLUSTER_NAME},
#             "pyspark_job": {
#                 "main_python_file_uri": "gs://{}/your_job_script.py".format(BUCKET_NAME),
#             },
#         }
#         operation = dataproc_client.submit_job(
#             project_id=os.environ["GOOGLE_CLOUD_PROJECT"],
#             region="your-region",
#             job=job_details
#         )
#         result = operation.result()

#         # Return the result
#         return {"message": "Data processing job submitted successfully."}

#     except Exception as e:
#         # Handle any errors
#         raise HTTPException(status_code=500, detail=str(e))
