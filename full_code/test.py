import boto3
import json

llamaModelId = 'meta.llama2-13b-chat-v1' 
prompt = "Just make the following SQL compatible with PostGreSQL? Just provide the output query only without any explaination. \n create table t1 (a int); "

llamaPayload = json.dumps({ 
	'prompt': prompt,
    'max_gen_len': 512,
	'top_p': 0.9,
	'temperature': 0.2
})

bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",
    aws_access_key_id="AKIAVRUVPPCQXOMUFMNP",
    aws_secret_access_key="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"
    )
response = bedrock_runtime.invoke_model(
    body=llamaPayload, 
    modelId=llamaModelId, 
    accept='application/json', 
    contentType='application/json'
)
body = response.get('body').read().decode('utf-8')
response_body = json.loads(body)
print(response_body['generation'].strip())