import math
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
import aws_controller

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
        return [serialize(v) for v in data]

    if isinstance(data, dict):
        try:
            return serializer.serialize(data)
        except TypeError:
            return {k: serialize(v) for k, v in data.items()}
    else:
        return data

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

    return valid_crags = list(valid_crags_iterator)

