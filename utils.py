import math
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
import aws_controller
import os
import requests
import datetime
from decimal import Decimal

deserializer = TypeDeserializer()
serializer = TypeSerializer()

# converts dynamodb object to list/dict
def deserialize(data):
    if isinstance(data, list):
        return [deserialize(v) for v in data]

    if isinstance(data, dict):
        try:
            return deserializer.deserialize(data)
        except TypeError:
            return {k: deserialize(v) for k, v in data.items()}
    else:
        return data

# converts list/dict to dynamodb object
def serialize(data):
    if isinstance(data, list):
        return {'L':[serialize(v) for v in data]}

    if isinstance(data, dict):
        try:
            return serializer.serialize(data)
        except TypeError:
            return {k: serialize(v) for k, v in data.items()}
    else:
        return serializer.serialize(Decimal(str(data)) if isinstance(data, float) else data)

# calculates distance between 2 lat,long coordinates
def getDistanceFromLatLonInKm(lat1, lon1, lat2, lon2):
  R = 6371 # Radius of the earth in km
  dLat = math.radians(lat2 - lat1)
  dLon = math.radians(lon2 - lon1)
  a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2) * math.sin(dLon / 2)
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
  d = R * c # Distance in km
  return d

# returns list of crags with matching style and locations within radius
def getAndFilterCrags(lat, lon, radius, style):
    # get all crags of matching climbing_style
    allCrags = aws_controller.get_crags(style)
    # deserialize response
    deserializedData = deserialize(allCrags)

    matchingCrags = deserializedData['Items']

    def check_distance(crag):
        distance = getDistanceFromLatLonInKm(float(lat), float(lon), float(crag['lat']), float(crag['long']))

        if distance < int(radius):
            crag['distance'] = int(distance)
            return True
        return False

    valid_crags_iterator = filter(check_distance, matchingCrags)

    return list(valid_crags_iterator)

def addWeatherToCrags(crags):
    meteoblueApiKey = os.environ['METEOBLUE_API_KEY']

    for crag in crags:
        if 'time_last_weather' not in crag: # TODO if || crag['time_last_weather'] < some hours ago
            weatherResponse = requests.get('https://my.meteoblue.com/packages/basic-day', params={'apikey': meteoblueApiKey, 'lat': crag['lat'], 'lon': crag['long'], 'format': 'json'}).json()

            if 'data_day' in weatherResponse:
                crag['time_last_weather'] = datetime.datetime.now(datetime.timezone.utc).isoformat()

                cragToPut = serialize(crag)
                cragToPut['M']['weather_data'] = {'M': serialize(weatherResponse['data_day'])}
                putRes = aws_controller.put_crag(cragToPut['M'])

                crag['weather_data'] = weatherResponse['data_day']
