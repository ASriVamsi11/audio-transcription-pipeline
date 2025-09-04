import boto3, os
from datetime import datetime, timezone

s3 = boto3.client("s3")
dynamo = boto3.client("dynamodb")

def lambda_handler(event, context):
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']

    filename = os.path.basename(key)  # e.g. "79eb4774-15a0-4fcd.json" or "transcribe-79eb4774.json"

    # Handle both formats
    if filename.startswith("transcribe-"):
        file_id = filename.replace("transcribe-", "").replace(".json", "")
    else:
        file_id = filename.replace(".json", "")

    # Update DynamoDB
    try:
        dynamo.update_item(
            TableName="Transcriptions",
            Key={"file_id": {"S": file_id}},
            UpdateExpression="SET #s = :s, transcript_s3 = :t, updated_at = :u",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={
                ":s": {"S": "completed"},
                ":t": {"S": f"s3://{bucket}/{key}"},
                ":u": {"S": str(datetime.now(timezone.utc))}
            }
        )
        print(f"✅ Updated DynamoDB for {file_id}")
    except Exception as e:
        print(f"❌ Failed to update DynamoDB: {e}")

    return {"message": f"Processed {file_id}"}
