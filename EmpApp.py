from unittest import result
from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
import webbrowser

from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddEmp.html')


@app.route("/addemp", methods=['POST'])
def AddEmp():
    empid = request.form['empid']
    name = request.form['name']
    gender = request.form['gender']
    phone = request.form['phone']
    location = request.form['location']
    rate_per_day = request.form['rate_per_day']
    position = request.form['position']
    hire_date = request.form['hire_date']

    image = request.files['image']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if image.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (empid, name, gender, phone,
                       location, rate_per_day, position, hire_date))
        db_conn.commit()
        # Uplaod image file in S3 #
        image_name_in_s3 = "empid-" + str(empid) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(
                Key=image_name_in_s3, Body=image)
            bucket_location = boto3.client(
                's3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])
            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                image_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=name)

# @app.route("/getemp", methods=['GET', 'POST'])
# def getEmp():
#     return render_template('GetEmp.html')


@app.route("/fetchdata", methods=['GET', 'POST'])
def FetchData():
    cursor = db_conn.cursor()
    cursor.execute('Select * from employee')
    results = cursor.fetchall()
    print(results)

    empid = []
    name = []
    gender = []
    phone = []
    location = []
    rate = []
    position = []
    hire_date = []

    for row in results:
        empid.append(row[0])
        name.append(row[1])
        gender.append(row[2])
        phone.append(row[3])
        location.append(row[4])
        rate.append(row[5])
        position.append(row[6])
        hire_date.append(row[7])

    return render_template(
        'GetEmpOutput.html',
        results=results,
        empid=empid,
        name=name,
        gender=gender,
        phone=phone,
        location=location,
        rate=rate,
        position=position,
        hire_date=hire_date,
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
