import streamlit as st
import boto3
import json


st.title("Building with Bedrock")  # Title of the application
st.subheader("Image Generation Demo")

REGION = "us-east-1"

# List of Stable Diffusion Preset Styles
sd_presets = [
    "None",
    "3d-model",
    "analog-film",
    "anime",
    "cinematic",
    "comic-book",
    "digital-art",
    "enhance",
    "fantasy-art",
    "isometric",
    "line-art",
    "low-poly",
    "modeling-compound",
    "neon-punk",
    "origami",
    "photographic",
    "pixel-art",
    "tile-texture",
]

# Define bedrock
bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    #region_name=REGION,                                                # My AWS Credential
    #aws_access_key_id="AKIAVRUVPPCQXOMUFMNP",                          # My AWS Credential
    #aws_secret_access_key="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"   # My AWS Credential
    region_name="us-east-1",                                            # ACloudGuru Credential
    aws_access_key_id="AKIATIHF5666J3EIFVB6",                           # ACloudGuru Credential
    aws_secret_access_key="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"    # ACloudGuru Credential
)


# Bedrock api call to stable diffusion
def generate_image_sd(text, style):
    """
    Purpose:
        Uses Bedrock API to generate an Image
    Args/Requests:
         text: Prompt
         style: style for image
    Return:
        image: base64 string of image
    """
    body = {
        "text_prompts": [{"text": text}],
        "cfg_scale": 10,
        "seed": 0,
        "steps": 50,
        "style_preset": style,
    }

    if style == "None":
        del body["style_preset"]

    body = json.dumps(body)

    modelId = "stability.stable-diffusion-xl"
    accept = "application/json"
    contentType = "application/json"

    response = bedrock_runtime.invoke_model(
        body=body, modelId=modelId, accept=accept, contentType=contentType
    )
    response_body = json.loads(response.get("body").read())

    results = response_body.get("artifacts")[0].get("base64")
    return results


def generate_image_titan(text):
    """
    Purpose:
        Uses Bedrock API to generate an Image using Titan
    Args/Requests:
         text: Prompt
    Return:
        image: base64 string of image
    """
    body = {
        "textToImageParams": {"text": text},
        "taskType": "TEXT_IMAGE",
        "imageGenerationConfig": {
            "cfgScale": 10,
            "seed": 0,
            "quality": "standard",
            "width": 512,
            "height": 512,
            "numberOfImages": 1,
        },
    }

    body = json.dumps(body)

    modelId = "amazon.titan-image-generator-v1"
    accept = "application/json"
    contentType = "application/json"

    response = bedrock_runtime.invoke_model(
        body=body, modelId=modelId, accept=accept, contentType=contentType
    )
    response_body = json.loads(response.get("body").read())

    results = response_body.get("images")[0]
    return results

import streamlit as st
import boto3, io
import json
from PIL import Image
import base64

# Existing code

# 1. Add text input
prompt = st.text_input("Enter Prompt")

# 2. Add style select if Stable Diffusion 
model = st.selectbox("Select Model", ["Stable Diffusion", "Amazon Titan"])
if model == "Stable Diffusion":
  style = st.selectbox("Select Style", sd_presets)

# 3. Function to convert base64 to image
def base64_to_image(base64_str):
  imgdata = base64.b64decode(base64_str)
  return Image.open(io.BytesIO(imgdata))

# 4. Generate button  
if st.button("Generate"):

  # Call appropriate generation function
  if model == "Amazon Titan":
    image_b64 = generate_image_titan(prompt)
  else:  
    image_b64 = generate_image_sd(prompt, style)  

  # 5. Convert base64 to PIL image  
  image = base64_to_image(image_b64)

  st.image(image)
