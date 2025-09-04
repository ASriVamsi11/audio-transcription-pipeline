from datetime import datetime, timezone
import boto3, uuid
import os
s3 = boto3.client("s3")
dynamo = boto3.client("dynamodb")
transcribe = boto3.client("transcribe")

def lambda_handler(event, context):
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']
    file_id = str(uuid.uuid4())

    dynamo.put_item(
        TableName="Transcriptions",
        Item={
            "file_id": {"S": file_id},
            "filename": {"S": key},
            "status": {"S": "processing"},
            "created_at": {"S": str(datetime.now(timezone.utc))}
        }
    )
    
    job_name = f"transcribe-{file_id}"
    region = os.environ["AWS_REGION"]  # auto-pick Lambda region
    media_uri = f"https://s3.{region}.amazonaws.com/{bucket}/{key}"

    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={"MediaFileUri": media_uri},
        MediaFormat=key.split(".")[-1],
        LanguageCode="en-US",
        OutputBucketName=bucket,
        OutputKey=f"processed/{file_id}.json"
    )

    return {"status": "started", "file_id": file_id}
