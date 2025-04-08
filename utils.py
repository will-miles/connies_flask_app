import math
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

deserializer = TypeDeserializer()
serializer = TypeSerializer()

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

def serialize(data):
    if isinstance(data, list):
        return [serialize(v) for v in data]

    if isinstance(data, dict):
        try:
            return serializer.serialize(data)
        except TypeError:
            return {k: serialize(v) for k, v in data.items()}
    else:
        return data

def getDistanceFromLatLonInKm(lat1, lon1, lat2, lon2):
  R = 6371 # Radius of the earth in km
  dLat = math.radians(lat2 - lat1) # math.radians below
  dLon = math.radians(lon2 - lon1)
  a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2) * math.sin(dLon / 2)
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
  d = R * c # Distance in km
  return d
