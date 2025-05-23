import boto3
import os
from botocore.exceptions import ClientError
import ast

region_name = 'us-east-1'
dynamo_client = boto3.client('dynamodb', region_name=region_name)

def get_secret(secret_name):
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    secret = get_secret_value_response['SecretString']
    return ast.literal_eval(secret)


def get_crags(style):
    return dynamo_client.query(
        TableName='crags',
        KeyConditionExpression='climbing_style = :climbing_style',
        ExpressionAttributeValues={":climbing_style":{"S": style}},
    )

def put_crag(crag):
    return dynamo_client.put_item(
        TableName='crags',
        Item=crag
    )