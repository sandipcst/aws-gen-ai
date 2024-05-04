import boto3
import json, os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

PromptBucket = os.environ['PROMPT_BUCKET']
PromptFile = os.environ['PROMPT_FILE']
queue_url = os.environ['QUEUE_URL']

def read_prompt_from_s3(bucket_name, object_key):
    s3 = boto3.client('s3')
    try:
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        prompt_content = response['Body'].read().decode('utf-8')
        return prompt_content
    except Exception as e:
        print(f"Error reading prompt file from S3: {e}")
        return None


def generate_text(model_id, body):
    """
    Generate text using Amazon Bedrock Llama model on demand.
    Args:
        model_id (str): The model ID to use.
        body (str) : The request body to use.
    Returns:
        response (json): The response from the model.
    """
    logger.info("Generating text with Amazon Bedrock Llama model %s", model_id)

    bedrock = boto3.client(
        service_name="bedrock-runtime",
        region_name="us-east-1",
        aws_access_key_id="AKIAUDYK5RDSUYQYGFXW",
        aws_secret_access_key="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"
    )

    accept = "application/json"
    content_type = "application/json"

    response = bedrock.invoke_model(
        body=body, modelId=model_id, accept=accept, contentType=content_type
    )
    response_body = json.loads(response.get("body").read().decode('utf-8'))

    finish_reason = response_body.get("error")

    if finish_reason is not None:
        raise ImageError(f"Text generation error. Error is {finish_reason}")

    logger.info("Successfully generated text with Amazon Bedrock Llama model %s", model_id)

    return response_body

def lambda_handler(event, context):
    sqs = boto3.client('sqs')
    
    # Get the SQS queue URL from environment variables
    #queue_url = os.environ['QUEUE_URL']
    
    # Receive messages from the SQS queue
    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=10,  # Adjust the number of messages to retrieve as needed
        WaitTimeSeconds=20  # Adjust the wait time as needed
    )
    
    #model_id = 'meta.llama2-13b-chat-v1'
    model_id = 'amazon.titan-text-express-v1'
    targetDb="MongoDB"
    #prompt = "Just make the following SQL compatible with" +targetDb+"? Just provide the output query only without any explaination. \n"
    prompt = read_prompt_from_s3(PromptBucket, PromptFile)

    # Check if there are any messages
    if 'Messages' in response:
        for message in response['Messages']:
            # Get the body of the message
            body = json.loads(message['Body'])
            # Get the bucket name and object key from the message
            bucket = body['Records'][0]['s3']['bucket']['name']
            key = body['Records'][0]['s3']['object']['key']
            # Get the object from S3
            s3 = boto3.client('s3')
            response = s3.get_object(Bucket=bucket, Key=key)
            data = response['Body'].read().decode('utf-8')
            # Split SQL statements using semicolon (;) delimiter
            sql_statements = data.split(';')
            # Initialize an empty list to store converted SQL statements
            converted_sql_statements = []
            # Loop through each SQL statement and convert using the Bedrock Llama model
            for sql in sql_statements:
                # Ignore empty statements
                if sql.strip():
                    # Generate text using Bedrock Llama model
                    #body = json.dumps({
                        #"prompt": prompt+" "+sql,
                        #'max_gen_len': 2048,
                        #'top_p': 0.9,
                        #'temperature': 0.5

                    #})
                    body = json.dumps({
                        "inputText": "User: "+prompt+" "+sql+"\nBot:",
                        "textGenerationConfig": {
                            "maxTokenCount": 2048,
                            "stopSequences": [],
                            "temperature": 0,
                            "topP": 0.1
                        }
                    })
                    print("Given prompt - "+body)
                    converted_sql = generate_text(model_id, body)
                    print(converted_sql)
                    
                    #if model_id == 'meta.llama2-13b-chat-v1':
                        #output = converted_sql['generation'].strip()
                    if model_id == 'amazon.titan-text-express-v1':
                        output = ''
                        for result in converted_sql['results']:
                            output += result['outputText']
                            
                    converted_sql_statements.append(output)
            # Delete the message from the SQS queue
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=message['ReceiptHandle']
            )
    #print(converted_sql_statements)
    return converted_sql_statements
