from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
import logging

app = Flask(__name__)

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Configuration
DBHOST = os.environ.get("DBHOST", "localhost")
DBUSER = os.environ.get("DBUSER")
DBPWD = os.environ.get("DBPWD")
DATABASE = os.environ.get("DATABASE", "employees")
DBPORT = int(os.environ.get("DBPORT", 3306))

# Background Image Configuration
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
BACKGROUND_IMAGE = os.environ.get("BACKGROUND_IMAGE", "default.jpg")
DEVELOPER_NAME = os.environ.get("DEVELOPER_NAME", "Default Developer")

# S3 Client for Background Images
s3_client = boto3.client('s3')

# Database Connection
db_conn = connections.Connection(
    host=DBHOST,
    port=DBPORT,
    user=DBUSER,
    password=DBPWD, 
    db=DATABASE
)

# Background Image Download Function
def download_background_image():
    try:
        # Ensure static/background directory exists
        os.makedirs("static/background", exist_ok=True)
        
        # Log background image details
        logger.info(f"Downloading background image: {BACKGROUND_IMAGE}")
        logger.info(f"From S3 Bucket: {S3_BUCKET_NAME}")
        
        # Download image to local static folder
        local_path = f"static/background/{BACKGROUND_IMAGE}"
        s3_client.download_file(S3_BUCKET_NAME, BACKGROUND_IMAGE, local_path)
        
        logger.info(f"Successfully downloaded background image: {BACKGROUND_IMAGE}")
        return f"/static/background/{BACKGROUND_IMAGE}"
    except Exception as e:
        logger.error(f"Error downloading background image: {e}")
        return None

# Routes
@app.route("/", methods=['GET', 'POST'])
def home():
    background_image = download_background_image()
    return render_template('addemp.html', 
                           background_image=background_image,
                           developer_name=DEVELOPER_NAME)

@app.route("/addemp", methods=['POST'])
def AddEmp():
    background_image = download_background_image()
    
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    primary_skill = request.form['primary_skill']
    location = request.form['location']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        cursor.execute(insert_sql, (emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
        emp_name = f"{first_name} {last_name}"
    except Exception as e:
        logger.error(f"Error inserting employee: {e}")
        emp_name = "Error occurred"
    finally:
        cursor.close()

    return render_template('addempoutput.html', 
                           name=emp_name, 
                           background_image=background_image,
                           developer_name=DEVELOPER_NAME)

@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    background_image = download_background_image()
    return render_template("getemp.html", 
                           background_image=background_image,
                           developer_name=DEVELOPER_NAME)

@app.route("/fetchdata", methods=['GET','POST'])
def FetchData():
    background_image = download_background_image()
    
    emp_id = request.form['emp_id']
    output = {}

    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location from employee where emp_id=%s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (emp_id))
        result = cursor.fetchone()
        
        if result:
            output["emp_id"] = result[0]
            output["first_name"] = result[1]
            output["last_name"] = result[2]
            output["primary_skills"] = result[3]
            output["location"] = result[4]
        else:
            logger.warning(f"No employee found with ID: {emp_id}")
    except Exception as e:
        logger.error(f"Error fetching employee data: {e}")
    finally:
        cursor.close()

    return render_template("getempoutput.html", 
                           id=output.get("emp_id", "N/A"),
                           fname=output.get("first_name", "N/A"),
                           lname=output.get("last_name", "N/A"),
                           interest=output.get("primary_skills", "N/A"), 
                           location=output.get("location", "N/A"), 
                           background_image=background_image,
                           developer_name=DEVELOPER_NAME)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81, debug=True)