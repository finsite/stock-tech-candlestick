import json
import os
import time

import boto3
import pika
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


def connect_to_rabbitmq() -> pika.BlockingConnection:
    """Creates and returns a RabbitMQ connection with retries.

    Establishes a connection to RabbitMQ and returns the connection object.
    If the connection fails, it will retry up to 5 times with 5 seconds between retries.
    If all retries fail, it will raise a ConnectionError.

    :returns pika.BlockingConnection: A RabbitMQ connection object
    :raises ConnectionError: If the connection to RabbitMQ fails after multiple attempts
    """
    retries: int = 5  # Number of retry attempts
    while retries > 0:
        try:
            connection_params: pika.ConnectionParameters = pika.ConnectionParameters(
                host=RABBITMQ_HOST
            )
            connection: pika.BlockingConnection = pika.BlockingConnection(connection_params)
            if connection.is_open:
                logger.info("Connected to RabbitMQ")
                return connection
            else:
                logger.error("Failed to open RabbitMQ connection")
        except (pika.exceptions.AMQPConnectionError, Exception) as e:
            retries -= 1
            logger.warning(
                "Failed to connect to RabbitMQ (%s), retrying in 5s...",
                str(e),
            )
            time.sleep(5)
    logger.error("Could not connect to RabbitMQ after multiple attempts")
    raise ConnectionError("RabbitMQ connection failed")


def consume_rabbitmq() -> None:
    """Consumes messages from RabbitMQ, processes them, and sends output.

    Establishes a connection to RabbitMQ, declares an exchange, queue, and binding,
    and starts consuming messages. The messages are processed by the `analyze`
    function and the resulting data is sent to the output handler.

    If an error occurs while processing a message, it will be logged and either
    requeued (if the error is transient) or discarded (if the error is due to
    invalid input).

    This function is designed to be stopped by a KeyboardInterrupt signal, such as
    a Ctrl+C event. When stopped, the RabbitMQ connection is closed and any
    remaining messages are acknowledged.

    Returns
    -------
        None

    """
    connection: pika.BlockingConnection = connect_to_rabbitmq()
    channel: pika.adapters.blocking_connection.BlockingChannel = connection.channel()

    # Declare exchange, queue, and binding
    channel.exchange_declare(exchange=RABBITMQ_EXCHANGE, exchange_type="topic", durable=True)
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    channel.queue_bind(
        exchange=RABBITMQ_EXCHANGE,
        queue=RABBITMQ_QUEUE,
        routing_key=RABBITMQ_ROUTING_KEY,
    )

    def callback(
        ch: pika.adapters.blocking_connection.BlockingChannel,
        method: pika.spec.Basic.Deliver,
        properties: pika.spec.BasicProperties,
        body: bytes,
    ) -> None:
        """Callback function for processing received messages from RabbitMQ.

        This function is triggered for each message received from RabbitMQ. It
        attempts to decode the message body from JSON and processes it using the
        `analyze` function. If successful, it sends the processed result to the
        output handler and acknowledges the message. If a JSON decoding error
        occurs, the message is logged and discarded. For other exceptions, the
        error is logged and the message is requeued for retry.

        Args:
        ----
            ch (pika.adapters.blocking_connection.BlockingChannel): The channel object.
            method (pika.spec.Basic.Deliver): The delivery method associated with the message.
            properties (pika.spec.BasicProperties): The properties of the message.
            body (bytes): The message body received from RabbitMQ.

        Returns:
        -------
            None

        """
        try:
            # Parse the message body as JSON
            message = json.loads(body)
            logger.info("Received message: %s", message)

            # Analyze the message data and send the result to the output handler
            result = analyze(message)
            send_to_output(result)

            # Acknowledge successful processing of the message
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except json.JSONDecodeError:
            # Log JSON decoding errors and discard the message
            logger.error("Invalid JSON format: %s", body)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            # Log other processing errors and requeue the message for retry
            logger.error("Error processing message: %s", e)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

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


def consume_sqs() -> None:
    """Consumes messages from AWS SQS, processes them, and sends output.

    This function continuously polls the specified SQS queue for messages,
    processes them using the `analyze` function, and sends the processed data
    to the output handler. If an error occurs while processing a message, it
    will be logged and the message will be deleted from the queue.

    If the SQS client is not initialized or if the queue URL is not provided,
    the function will log an error and do nothing.

    :return: None
    """
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
                    sqs_client.delete_message(
                        QueueUrl=SQS_QUEUE_URL, ReceiptHandle=message["ReceiptHandle"]
                    )
                    logger.info("Deleted SQS message: %s", message["MessageId"])

                except json.JSONDecodeError:
                    logger.error("Invalid JSON format in SQS message: %s", message["Body"])
                except Exception as e:
                    logger.error("Error processing SQS message: %s", e)

        except (BotoCoreError, NoCredentialsError) as e:
            logger.error("Error receiving messages from SQS: %s", e)
            time.sleep(5)  # Wait before retrying


def consume_messages() -> None:
    """Determines the type of message queue specified by the `QUEUE_TYPE` environment
    variable and starts the appropriate consumer.

    The `QUEUE_TYPE` environment variable can be set to "rabbitmq" or "sqs" to
    select the type of message queue to use. If the variable is not set or is
    set to an invalid value, an error message will be logged and the function
    will do nothing.

    :return: None
    :raises ValueError: If the `QUEUE_TYPE` environment variable is not set or
        has an invalid value.
    """
    # Check the QUEUE_TYPE environment variable and invoke the corresponding consumer
    if QUEUE_TYPE == "rabbitmq":
        # Start consuming messages from RabbitMQ
        consume_rabbitmq()
    elif QUEUE_TYPE == "sqs":
        # Start consuming messages from SQS
        consume_sqs()
    else:
        # Log an error if an invalid QUEUE_TYPE is specified
        logger.error("Invalid QUEUE_TYPE specified. Use 'rabbitmq' or 'sqs'.")
