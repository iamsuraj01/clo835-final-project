from flask import Flask, render_template, request
from pymysql import connections
import os
import random
import boto3  # New import for S3 interaction
import logging  # New import for logging

app = Flask(__name__)

# Updated environment variables
DBHOST = os.environ.get("DBHOST", "localhost")
DBUSER = os.environ.get("DBUSER", "root")
DBPWD = os.environ.get("DBPWD", "password")
DATABASE = os.environ.get("DATABASE", "employees")
BACKGROUND_IMAGE = os.environ.get("BACKGROUND_IMAGE", "default.jpg")
DEVELOPER_NAME = os.environ.get("DEVELOPER_NAME", "CLO835 Student")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# S3 client for background image
s3_client = boto3.client('s3')

# Create a connection to the MySQL database
db_conn = connections.Connection(
    host=DBHOST,
    port=int(os.environ.get("DBPORT", 3306)),
    user=DBUSER,
    password=DBPWD, 
    db=DATABASE
)

# Function to download image from S3
def download_background_image():
    try:
        # Assume bucket and image details come from environment or ConfigMap
        bucket_name = os.environ.get("S3_BUCKET_NAME")
        image_key = BACKGROUND_IMAGE
        
        # Download image to local static folder
        local_path = f"static/background/{image_key}"
        s3_client.download_file(bucket_name, image_key, local_path)
        
        logger.info(f"Downloaded background image: {image_key} from bucket {bucket_name}")
        return f"/static/background/{image_key}"
    except Exception as e:
        logger.error(f"Error downloading background image: {e}")
        return None

# Rest of the existing code remains similar...

@app.route("/", methods=['GET', 'POST'])
def home():
    # Get background image URL
    background_image_url = download_background_image()
    
    return render_template('addemp.html', 
                           developer_name=DEVELOPER_NAME, 
                           background_image=background_image_url)
                           
    return render_template('addempoutput.html', 
                           developer_name=DEVELOPER_NAME, 
                           background_image=background_image_url)
    
    return render_template('getemp.html', 
                           developer_name=DEVELOPER_NAME, 
                           background_image=background_image_url)
                           
    return render_template('getempoutput.html', 
                           developer_name=DEVELOPER_NAME, 
                           background_image=background_image_url)

if __name__ == '__main__':
    # Updated to listen on port 81
    app.run(host='0.0.0.0', port=81, debug=True)