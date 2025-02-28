import json
import os
import time
import pika
import boto3
from botocore.exceptions import BotoCoreError, NoCredentialsError

from app.logger import logger
from app.output_handler import send_to_output
from app.processor import analyze

# Environment variables for queue type selection
QUEUE_TYPE = os.getenv("QUEUE_TYPE", "rabbitmq").lower()  # Options: 'rabbitmq' or 'sqs'

# RabbitMQ settings
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "stock_analysis")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "analysis_queue")
RABBITMQ_ROUTING_KEY = os.getenv("RABBITMQ_ROUTING_KEY", "#")

# SQS settings
SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL", "")
SQS_REGION = os.getenv("SQS_REGION", "us-east-1")

# Initialize SQS client (if needed)
sqs_client = None
if QUEUE_TYPE == "sqs":
    try:
        sqs_client = boto3.client("sqs", region_name=SQS_REGION)
        logger.info(f"SQS client initialized for region {SQS_REGION}")
    except (BotoCoreError, NoCredentialsError) as e:
        logger.error("Failed to initialize SQS client: %s", e)
        sqs_client = None


def connect_to_rabbitmq():
    """Creates and returns a RabbitMQ connection with retries."""
    retries = 5
    while retries > 0:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            logger.info("Connected to RabbitMQ")
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            retries -= 1
            logger.warning("Failed to connect to RabbitMQ (%s), retrying in 5s...", e)
            time.sleep(5)
    logger.error("Could not connect to RabbitMQ after multiple attempts")
    raise ConnectionError("RabbitMQ connection failed")


def consume_rabbitmq():
    """Consumes messages from RabbitMQ, processes them, and sends output."""
    connection = connect_to_rabbitmq()
    channel = connection.channel()
    
    # Declare exchange, queue, and binding
    channel.exchange_declare(exchange=RABBITMQ_EXCHANGE, exchange_type="topic", durable=True)
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    channel.queue_bind(exchange=RABBITMQ_EXCHANGE, queue=RABBITMQ_QUEUE, routing_key=RABBITMQ_ROUTING_KEY)

    def callback(ch, method, properties, body):
        """Processes received messages and acknowledges them."""
        try:
            message = json.loads(body)
            logger.info("Received message: %s", message)

            result = analyze(message)  # Process the data
            send_to_output(result)  # Send processed data

            ch.basic_ack(delivery_tag=method.delivery_tag)  # Acknowledge message
        except json.JSONDecodeError:
            logger.error("Invalid JSON format: %s", body)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)  # Do not retry
        except Exception as e:
            logger.error("Error processing message: %s", e)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)  # Retry message

    # Set up consumer
    channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback)

    logger.info("Waiting for messages from RabbitMQ...")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("Stopping RabbitMQ message consumption...")
        channel.stop_consuming()
    finally:
        connection.close()
        logger.info("RabbitMQ connection closed.")


def consume_sqs():
    """Consumes messages from AWS SQS, processes them, and sends output."""
    if not sqs_client or not SQS_QUEUE_URL:
        logger.error("SQS client is not initialized or missing queue URL.")
        return

    logger.info("Polling for messages from SQS...")

    while True:
        try:
            response = sqs_client.receive_message(
                QueueUrl=SQS_QUEUE_URL,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=10,  # Long polling
            )

            if "Messages" not in response:
                continue  # No messages received, continue polling

            for message in response["Messages"]:
                try:
                    body = json.loads(message["Body"])
                    logger.info("Received SQS message: %s", body)

                    result = analyze(body)  # Process the data
                    send_to_output(result)  # Send processed data

                    # Delete message after successful processing
                    sqs_client.delete_message(QueueUrl=SQS_QUEUE_URL, ReceiptHandle=message["ReceiptHandle"])
                    logger.info("Deleted SQS message: %s", message["MessageId"])

                except json.JSONDecodeError:
                    logger.error("Invalid JSON format in SQS message: %s", message["Body"])
                except Exception as e:
                    logger.error("Error processing SQS message: %s", e)

        except (BotoCoreError, NoCredentialsError) as e:
            logger.error("Error receiving messages from SQS: %s", e)
            time.sleep(5)  # Wait before retrying


def consume_messages():
    """Determines the queue type and starts the appropriate consumer."""
    if QUEUE_TYPE == "rabbitmq":
        consume_rabbitmq()
    elif QUEUE_TYPE == "sqs":
        consume_sqs()
    else:
        logger.error("Invalid QUEUE_TYPE specified. Use 'rabbitmq' or 'sqs'.")
