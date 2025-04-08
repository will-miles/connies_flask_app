import boto3

dynamo_client = boto3.client('dynamodb', region_name='us-east-1')

def get_crags(style):
    return dynamo_client.query(
    TableName='crags',
    KeyConditionExpression='climbing_style = :climbing_style',
    ExpressionAttributeValues={":climbing_style":{"S": style}},
    )