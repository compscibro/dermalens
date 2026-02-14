"""
DynamoDB Client Configuration
Automatically uses IAM role credentials when running on AWS
"""
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime
import uuid

from app.core.config import settings

logger = logging.getLogger(__name__)


class DynamoDBClient:
    """DynamoDB client with IAM role authentication"""
    
    def __init__(self):
        """
        Initialize DynamoDB client
        Automatically uses IAM role when running on AWS EC2/ECS/Lambda
        """
        # boto3 automatically uses IAM role credentials from the instance metadata
        # No need to provide access keys!
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=settings.AWS_REGION,
            endpoint_url=settings.AWS_DYNAMODB_ENDPOINT  # None for AWS, or local endpoint
        )
        
        # Table references
        self.users_table = self.dynamodb.Table(settings.DYNAMODB_USERS_TABLE)
        self.scans_table = self.dynamodb.Table(settings.DYNAMODB_SCANS_TABLE)
        self.plans_table = self.dynamodb.Table(settings.DYNAMODB_PLANS_TABLE)
        self.chat_table = self.dynamodb.Table(settings.DYNAMODB_CHAT_TABLE)
        
        logger.info(f"✅ DynamoDB client initialized (Region: {settings.AWS_REGION})")
        logger.info(f"   Using IAM role authentication (no access keys needed)")
    
    def create_tables_if_not_exist(self):
        """Create DynamoDB tables if they don't exist"""
        try:
            self._create_users_table()
            self._create_scans_table()
            self._create_plans_table()
            self._create_chat_table()
            logger.info("✅ All DynamoDB tables verified/created")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    def _create_users_table(self):
        """Create users table"""
        try:
            self.users_table.load()
            logger.info(f"Table {settings.DYNAMODB_USERS_TABLE} exists")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.info(f"Creating table {settings.DYNAMODB_USERS_TABLE}...")
                table = self.dynamodb.create_table(
                    TableName=settings.DYNAMODB_USERS_TABLE,
                    KeySchema=[
                        {'AttributeName': 'user_id', 'KeyType': 'HASH'},  # Partition key
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'user_id', 'AttributeType': 'S'},
                        {'AttributeName': 'email', 'AttributeType': 'S'},
                    ],
                    GlobalSecondaryIndexes=[
                        {
                            'IndexName': 'email-index',
                            'KeySchema': [
                                {'AttributeName': 'email', 'KeyType': 'HASH'}
                            ],
                            'Projection': {'ProjectionType': 'ALL'},
                            'ProvisionedThroughput': {
                                'ReadCapacityUnits': 5,
                                'WriteCapacityUnits': 5
                            }
                        }
                    ],
                    ProvisionedThroughput={
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                )
                table.wait_until_exists()
                logger.info(f"✅ Created {settings.DYNAMODB_USERS_TABLE}")
    
    def _create_scans_table(self):
        """Create scans table"""
        try:
            self.scans_table.load()
            logger.info(f"Table {settings.DYNAMODB_SCANS_TABLE} exists")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.info(f"Creating table {settings.DYNAMODB_SCANS_TABLE}...")
                table = self.dynamodb.create_table(
                    TableName=settings.DYNAMODB_SCANS_TABLE,
                    KeySchema=[
                        {'AttributeName': 'user_id', 'KeyType': 'HASH'},  # Partition key
                        {'AttributeName': 'scan_id', 'KeyType': 'RANGE'},  # Sort key
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'user_id', 'AttributeType': 'S'},
                        {'AttributeName': 'scan_id', 'AttributeType': 'S'},
                        {'AttributeName': 'scan_date', 'AttributeType': 'S'},
                    ],
                    LocalSecondaryIndexes=[
                        {
                            'IndexName': 'scan-date-index',
                            'KeySchema': [
                                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                                {'AttributeName': 'scan_date', 'KeyType': 'RANGE'}
                            ],
                            'Projection': {'ProjectionType': 'ALL'}
                        }
                    ],
                    ProvisionedThroughput={
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                )
                table.wait_until_exists()
                logger.info(f"✅ Created {settings.DYNAMODB_SCANS_TABLE}")
    
    def _create_plans_table(self):
        """Create treatment plans table"""
        try:
            self.plans_table.load()
            logger.info(f"Table {settings.DYNAMODB_PLANS_TABLE} exists")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.info(f"Creating table {settings.DYNAMODB_PLANS_TABLE}...")
                table = self.dynamodb.create_table(
                    TableName=settings.DYNAMODB_PLANS_TABLE,
                    KeySchema=[
                        {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                        {'AttributeName': 'plan_id', 'KeyType': 'RANGE'},
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'user_id', 'AttributeType': 'S'},
                        {'AttributeName': 'plan_id', 'AttributeType': 'S'},
                    ],
                    ProvisionedThroughput={
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                )
                table.wait_until_exists()
                logger.info(f"✅ Created {settings.DYNAMODB_PLANS_TABLE}")
    
    def _create_chat_table(self):
        """Create chat messages table"""
        try:
            self.chat_table.load()
            logger.info(f"Table {settings.DYNAMODB_CHAT_TABLE} exists")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.info(f"Creating table {settings.DYNAMODB_CHAT_TABLE}...")
                table = self.dynamodb.create_table(
                    TableName=settings.DYNAMODB_CHAT_TABLE,
                    KeySchema=[
                        {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                        {'AttributeName': 'message_id', 'KeyType': 'RANGE'},
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'user_id', 'AttributeType': 'S'},
                        {'AttributeName': 'message_id', 'AttributeType': 'S'},
                        {'AttributeName': 'session_id', 'AttributeType': 'S'},
                    ],
                    LocalSecondaryIndexes=[
                        {
                            'IndexName': 'session-index',
                            'KeySchema': [
                                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                                {'AttributeName': 'session_id', 'KeyType': 'RANGE'}
                            ],
                            'Projection': {'ProjectionType': 'ALL'}
                        }
                    ],
                    ProvisionedThroughput={
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                )
                table.wait_until_exists()
                logger.info(f"✅ Created {settings.DYNAMODB_CHAT_TABLE}")


# Singleton instance
dynamodb_client = DynamoDBClient()
