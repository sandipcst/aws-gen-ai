# Copyright 

import json
import logging
import boto3
import streamlit as st
from streamlit import button
import sqlvalidator


from botocore.exceptions import ClientError


class ImageError(Exception):
    "Custom exception for errors returned by Amazon &titan-text-express; model"

    def __init__(self, message):
        self.message = message


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def generate_text(model_id, body):
    """
    Generate text using Amazon &titan-text-express; model on demand.
    Args:
        model_id (str): The model ID to use.
        body (str) : The request body to use.
    Returns:
        response (json): The response from the model.
    """

    logger.info(
        "Generating text with Amazon &titan-text-express; model %s", model_id)

    # bedrock = boto3.client(service_name='bedrock-runtime')

    bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",
    aws_access_key_id="AKIAVRUVPPCQXOMUFMNP",
    aws_secret_access_key="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"
)

    accept = "application/json"
    content_type = "application/json"

    response = bedrock.invoke_model(
        body=body, modelId=model_id, accept=accept, contentType=content_type
    )
    response_body = json.loads(response.get("body").read())

    finish_reason = response_body.get("error")

    if finish_reason is not None:
        raise ImageError(f"Text generation error. Error is {finish_reason}")

    logger.info(
        "Successfully generated text with Amazon &titan-text-express; model %s", model_id)

    return response_body


def get_text_output(response_body):
    output = ''
    for result in response_body['results']:
        output += result['outputText']
        
    
    return output


def main():
    """
    Entrypoint for Amazon &titan-text-express; example.
    """
    try:
        logging.basicConfig(level=logging.INFO,
                            format="%(levelname)s: %(message)s")

        model_id = 'amazon.titan-text-express-v1'

        
        promptinput = st.text_input("Enter your SQL to convert")
        
        valid_sql = True

        sql = sqlvalidator.parse(promptinput)

        if sql.is_valid():
            valid_sql = True
        else:
            valid_sql = False

        targetDb = st.selectbox('Select target database:', ['Postgres SQL', 'MongoDB NoSQL statement', 'Oracle'])

        
        prompt = "Just make the following SQL compatible with" +targetDb+"? Just provide the output query only without any explaination."

        body = json.dumps({
            "inputText": prompt+" "+promptinput,
            "textGenerationConfig": {
                "maxTokenCount": 4096,
                "stopSequences": [],
                "temperature": 0,
                "topP": 1
            }
        })

        if st.button('Start Converting'):
            if valid_sql:
                # input is valid SQL, process query
            
                response_body = generate_text(model_id, body)
                output = get_text_output(response_body)
            else:
                # input is invalid
                output = "Invalid SQL entered. Please check your query and try again."
            st.write(output)


    except ClientError as err:
        message = err.response["Error"]["Message"]
        logger.error("A client error occurred: %s", message)
        print("A client error occured: " +
              format(message))
    except ImageError as err:
        logger.error(err.message)
        print(err.message)

    else:
        print(
            f"Finished generating text with the Amazon &titan-text-express; model {model_id}.")


if __name__ == "__main__":
    main()