import json
import os
import time

import boto3
import pika
from botocore.exceptions import BotoCoreError, NoCredentialsError
from pika.exceptions import AMQPConnectionError

from app.logger import setup_logger
from app.output_handler import send_to_output
from app.processor import analyze

# Initialize logger
logger = setup_logger(__name__)

# Environment variables for queue type selection
QUEUE_TYPE = os.getenv("QUEUE_TYPE", "rabbitmq").lower()  # Options: 'rabbitmq' or 'sqs'

# RabbitMQ settings
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "stock_analysis")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "analysis_queue")
RABBITMQ_ROUTING_KEY = os.getenv("RABBITMQ_ROUTING_KEY", "#")
RETRY_DELAY = int(os.getenv("RETRY_DELAY_SECONDS", "5"))

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


def connect_to_rabbitmq() -> pika.BlockingConnection:
    """"""
    retries = 5
    while retries > 0:
        try:
            connection_params = pika.ConnectionParameters(
                host=RABBITMQ_HOST, blocked_connection_timeout=30
            )
            connection = pika.BlockingConnection(connection_params)
            if connection.is_open:
                logger.info("Connected to RabbitMQ")
                return connection
            else:
                logger.error("Failed to open RabbitMQ connection")
        except (AMQPConnectionError, Exception) as e:
            retries -= 1
            logger.warning("Failed to connect to RabbitMQ (%s), retrying in 5s...", str(e))
            time.sleep(RETRY_DELAY)
    logger.error("Could not connect to RabbitMQ after multiple attempts")
    raise ConnectionError("RabbitMQ connection failed")


def consume_rabbitmq() -> None:
    """"""
    connection = connect_to_rabbitmq()
    channel = connection.channel()

    channel.exchange_declare(exchange=RABBITMQ_EXCHANGE, exchange_type="topic", durable=True)
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    channel.queue_bind(
        exchange=RABBITMQ_EXCHANGE,
        queue=RABBITMQ_QUEUE,
        routing_key=RABBITMQ_ROUTING_KEY,
    )

    def callback(ch, method, properties, body):
        """

        Args:
          ch: 
          method: 
          properties: 
          body: 

        Returns:

        """
        try:
            message = json.loads(body)
            logger.info("Received message: %s", message)
            result = analyze(message)
            send_to_output(result)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except json.JSONDecodeError:
            logger.error("Invalid JSON format: %s", body)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.error("Error processing message: %s", e)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

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


def consume_sqs() -> None:
    """"""
    if not sqs_client or not SQS_QUEUE_URL:
        logger.error("SQS client is not initialized or missing queue URL.")
        return

    logger.info("Polling for messages from SQS...")
    try:
        while True:
            try:
                response = sqs_client.receive_message(
                    QueueUrl=SQS_QUEUE_URL,
                    MaxNumberOfMessages=10,
                    WaitTimeSeconds=10,
                )
                if "Messages" not in response:
                    continue

                for message in response["Messages"]:
                    try:
                        body = json.loads(message["Body"])
                        logger.info("Received SQS message: %s", body)
                        result = analyze(body)
                        send_to_output(result)
                        sqs_client.delete_message(
                            QueueUrl=SQS_QUEUE_URL, ReceiptHandle=message["ReceiptHandle"]
                        )
                        logger.info("Deleted SQS message: %s", message.get("MessageId"))
                    except json.JSONDecodeError:
                        logger.error("Invalid JSON format in SQS message: %s", message["Body"])
                    except Exception as e:
                        logger.error("Error processing SQS message: %s", e)
            except (BotoCoreError, NoCredentialsError) as e:
                logger.error("Error receiving messages from SQS: %s", e)
                time.sleep(5)
    except KeyboardInterrupt:
        logger.info("Stopping SQS message polling...")


def consume_messages() -> None:
    """"""
    if QUEUE_TYPE == "rabbitmq":
        consume_rabbitmq()
    elif QUEUE_TYPE == "sqs":
        consume_sqs()
    else:
        logger.error("Invalid QUEUE_TYPE specified. Use 'rabbitmq' or 'sqs'.")
