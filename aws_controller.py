import boto3

dynamo_client = boto3.client('dynamodb', region_name='us-east-1')

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