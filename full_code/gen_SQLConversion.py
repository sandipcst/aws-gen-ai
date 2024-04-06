# Copyright 

import json
import logging
import boto3
import streamlit as st
#from streamlit import button
import sqlvalidator, sqlparse, re


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
    response_body = json.loads(response.get("body").read().decode('utf-8'))

    finish_reason = response_body.get("error")

    if finish_reason is not None:
        raise ImageError(f"Text generation error. Error is {finish_reason}")

    logger.info(
        "Successfully generated text with Amazon &titan-text-express; model %s", model_id)

    return response_body


def get_text_output(selectmodel,response_body):
    if selectmodel == 'Llama 2':
        output = response_body['generation'].strip()
    if selectmodel == 'Amazon Text Gen':
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

        #model_id = 'amazon.titan-text-express-v1'
        #model_id = 'meta.llama2-13b-chat-v1'


        
        promptinput = st.text_input("Enter your SQL to convert")
        
        valid_sql = True

        #sql = sqlvalidator.parse(promptinput)

        try:
            sqls = sqlparse.split(promptinput)
        except:
            valid_sql = False

        targetDb = st.selectbox('Select target database:', ['Postgres SQL', 'MongoDB NoSQL statement', 'Oracle'])

        selectmodel = st.selectbox('Select Model:', ['Amazon Text Gen', 'Llama 2'])

        if selectmodel == 'Amazon Text Gen':
            model_id = 'amazon.titan-text-express-v1'
        else:
            model_id = 'meta.llama2-13b-chat-v1'

        prompt = "Just make the following SQL compatible with" +targetDb+"? Just provide the output query only without any explaination. \n"

        output = []

        if st.button('Start Converting'):

            for sql in sqls:
                
                if selectmodel == 'Llama 2':
                    body = json.dumps({
                        "prompt": prompt+" "+sql,
                        'max_gen_len': 512,
                        'top_p': 0.9,
                        'temperature': 0.2

                    })
                
                if selectmodel == 'Amazon Text Gen':
                    body = json.dumps({
                        "inputText": prompt+" "+sql,
                        "textGenerationConfig": {
                            "maxTokenCount": 4096,
                            "stopSequences": [],
                            "temperature": 0,
                            "topP": 1
                        }
                    })

                if valid_sql:
                    # input is valid SQL, process query
                    response_body = generate_text(model_id, body)
                    output.append(get_text_output(selectmodel,response_body))
                else:
                    # input is invalid
                    output.append("Invalid SQL entered. Please check your query and try again.")
                #st.write(output)
        
        st.write(text for text in output)

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
