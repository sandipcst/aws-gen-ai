import streamlit as st
import boto3
import io

def upload_to_s3(files):
    # Replace 'example-315558256366' with your actual S3 bucket name
    bucket_name = 'example-315558256366'
    s3_client = boto3.client('s3')
    uploaded_file_names = []

    for file in files:
        with st.spinner(f'Uploading {file.name}...'):
            s3_client.upload_fileobj(file, bucket_name, file.name)
        uploaded_file_names.append(file.name)

    st.success('Files successfully uploaded to AWS S3!')
    return uploaded_file_names


def list_files_in_s3_bucket():
    # Replace 'output-315558256366' with your actual S3 bucket name
    bucket_name = 'output-315558256366'
    s3_client = boto3.client('s3')

    files = []
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix='converted_sql/')
        if 'Contents' in response:
            for obj in response['Contents']:
                files.append(obj['Key'])
    except Exception as e:
        st.error(f"An error occurred while listing files: {str(e)}")

    return files

def download_file_from_s3(file_name):
    # Replace 'output-315558256366' with your actual S3 bucket name
    bucket_name = 'output-315558256366'
    s3_client = boto3.client('s3')

    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=file_name)
        file_content = response['Body'].read()
        return file_content
    except Exception as e:
        st.error(f"An error occurred while downloading file: {str(e)}")

def main():
    st.set_page_config(layout="wide")  # Set the layout to wide mode

    st.title('File Uploader to AWS S3')

    files = st.file_uploader('Upload Files', type=['sql', 'ddl'], accept_multiple_files=True)

    if files:
        uploaded_file_names = upload_to_s3(files)
        st.write('Uploaded files:', uploaded_file_names)

    if st.button('Show Files'):
        files = list_files_in_s3_bucket()
        if files:
            for file_name in files:
                file_content = download_file_from_s3(file_name)
                st.subheader(f'File: {file_name}')
                st.code(file_content.decode('utf-8'))  # Use the full width for code display

                download_clicked = st.download_button(label=f'Download {file_name}', data=file_content, file_name=file_name, mime='text/plain')
                if download_clicked:
                    st.success(f'Downloaded {file_name}')
                st.write('---')  # Add a horizontal line for better separation

if __name__ == '__main__':
    main()
