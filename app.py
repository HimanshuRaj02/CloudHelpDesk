from flask import Flask, request, jsonify
import mysql.connector
import boto3
import mimetypes
from botocore.config import Config
from dotenv import load_dotenv
import os

load_dotenv()

S3_BUCKET = "cloudhelpdesk-attachments-977989887647-eu-north-1-an"

s3 = boto3.client(
    "s3",
    region_name="eu-north-1",
    config=Config(
        signature_version="s3v4",
        s3={"addressing_style": "virtual"}
    )
)

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


@app.route("/")
def home():
    return "CloudHelpDesk is running! CI/CD deployment successful."


@app.route("/tickets", methods=["GET"])
def get_tickets():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM tickets ORDER BY id DESC")
    tickets = cursor.fetchall()

    for ticket in tickets:
        if ticket["attachment"]:
            content_type, _ = mimetypes.guess_type(ticket["attachment"])

            ticket["attachment_url"] = s3.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": S3_BUCKET,
                    "Key": ticket["attachment"],
                    "ResponseContentDisposition": "inline",
                    "ResponseContentType": content_type or "application/octet-stream"
                },
                ExpiresIn=3600
            )

    cursor.close()
    connection.close()

    return jsonify(tickets)


@app.route("/tickets", methods=["POST"])
def create_ticket():
    data = request.get_json()

    title = data.get("title")
    priority = data.get("priority", "Medium")
    attachment = data.get("attachment")

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO tickets (title, priority, attachment) VALUES (%s, %s, %s)",
        (title, priority, attachment)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Ticket created successfully"
    }), 201

@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files.get("file")

    if not file:
        return jsonify({"error": "No file provided"}), 400

    s3.upload_fileobj(
        file,
        S3_BUCKET,
        file.filename
    )

    return jsonify({
        "message": "File uploaded successfully",
        "filename": file.filename
    }), 201
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
