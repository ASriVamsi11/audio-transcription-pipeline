from fastapi import FastAPI
import boto3, json

app = FastAPI()
dynamo = boto3.client("dynamodb")
s3 = boto3.client("s3")

TABLE_NAME = "Transcriptions"
BUCKET_NAME = "audio-transcription-pipeline-bucket"

@app.get("/")
def home():
    return {"message": "Audio Transcription Pipeline API is running"}

@app.get("/status/{file_id}")
def get_status(file_id: str):
    resp = dynamo.get_item(
        TableName=TABLE_NAME,
        Key={"file_id": {"S": file_id}}
    )
    if "Item" not in resp:
        return {"error": "Not found"}
    item = resp["Item"]
    return {
        "status": item["status"]["S"],
        "filename": item["filename"]["S"],
        "transcript_s3": item.get("transcript_s3", {}).get("S")
    }

@app.get("/transcript/{file_id}")
def get_transcript(file_id: str):
    key = f"processed/{file_id}.json"
    obj = s3.get_object(Bucket=BUCKET_NAME, Key=key)
    data = json.loads(obj["Body"].read().decode("utf-8"))
    text = data["results"]["transcripts"][0]["transcript"]
    return {"file_id": file_id, "transcript": text}