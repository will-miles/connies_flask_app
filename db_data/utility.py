import boto3
import json

stylesList = ['boulder', 'sport', 'trad', 'winter']

for style in stylesList:
  with open((style+'_crags.json'), 'r') as file:
    crags = file.read()

  parsed_crags = json.loads(crags)
  import_crags = []

  print(parsed_crags[0])

  for crag in parsed_crags:
    import_crags.append(
      {"aspect":{"S":crag['aspect']},
        "crag_name":{"S":crag['name']},
        "lat":{"S":crag['lat']},
        "long":{"S":crag['long']},
        "rock_type":{"S":crag['rockType']},
        "stared_routes":{"S":crag['numStaredClimbs']},
        "ukc_link": {"S":crag['ukcLink']},
        "climbing_style":{"S":style}})

  print([import_crags[1], import_crags[2]])

  dynamo_client = boto3.client('dynamodb', region_name='us-east-1')

  for crag in import_crags:
    response = dynamo_client.put_item(
    TableName='crags',
    Item=crag
  )