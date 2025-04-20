import math
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
import aws_controller
import os
import requests
from datetime import datetime, date, time, timezone
from decimal import Decimal
import pytz

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

    tz = pytz.timezone("Europe/London")
    the_date = date.today()
    midnight_without_tzinfo = datetime.combine(the_date, time())
    midnight_with_tzinfo = tz.localize(midnight_without_tzinfo)
    utc = midnight_with_tzinfo.astimezone(pytz.utc)

    for crag in crags:

        lastUpdated = datetime.fromisoformat(crag['time_last_weather'])
        midnightTodayUkUTC = midnight_with_tzinfo.astimezone(pytz.utc)

        if 'time_last_weather' not in crag or lastUpdated < midnightTodayUkUTC:

            print(lastUpdated)
            print(midnightTodayUK)

            weatherResponse = requests.get('https://my.meteoblue.com/packages/basic-day', params={'apikey': meteoblueApiKey, 'lat': crag['lat'], 'lon': crag['long'], 'format': 'json'}).json()

            if 'data_day' in weatherResponse:
                crag['time_last_weather'] = datetime.now(timezone.utc).isoformat()
                # crag['weather_data']['weather_score'] = calculateWeatherScore(crag)

                cragToPut = serialize(crag)
                cragToPut['M']['weather_data'] = {'M': serialize(weatherResponse['data_day'])}
                putRes = aws_controller.put_crag(cragToPut['M'])

                crag['weather_data'] = weatherResponse['data_day']

idealConditions = {
    'boulder': {
        'temp': 5,
        'wind': [3.4, 10.7],
        'precip': 0,
        'humidity': 20,
    },
    'sport': {
        'temp': 10,
        'wind': [3.4, 10.7],
        'precip': 0,
        'humidity': 20,
    },
    'trad': {
        'temp': 10,
        'wind': [3.4, 10.7],
        'precip': 0,
        'humidity': 20,
    },
    'winter': {
        'temp': -10,
        'wind': [0, 7.9],
        'precip': 0,
        'humidity': 20,
    }
}

def calculateWeatherScore(crag):
    weatherData = crag["weather_data"]
    ideals = idealConditions[crag["climbing_style"]]
    scoreList = []
    for index in list(range(0, 7)):
        score = 0
        # temp
        if (weatherData["temperature_max"][index] > (ideals["temp"]-2) and weatherData["temperature_max"][index] < (ideals["temp"]+2)):
            score += 5
        elif (weatherData["temperature_max"][index] > (ideals["temp"]-4) and weatherData["temperature_max"][index] < (ideals["temp"]+4)):
            score += 4
        elif (weatherData["temperature_max"][index] > (ideals["temp"]-6) and weatherData["temperature_max"][index] < (ideals["temp"]+6)):
            score += 3
        elif (weatherData["temperature_max"][index] > (ideals["temp"]-8) and weatherData["temperature_max"][index] < (ideals["temp"]+8)):
            score += 2
        elif (weatherData["temperature_max"][index] > (ideals["temp"]-10) and weatherData["temperature_max"][index] < (ideals["temp"]+10)):
            score += 1

        # precip
        if (weatherData["precipitation"][index] <= (ideals["precip"])):
            score += 5
        elif (weatherData["precipitation"][index] <= (ideals["precip"]+2)):
            score += 4
        elif (weatherData["precipitation"][index] <= (ideals["precip"]+4)):
            score += 3
        elif (weatherData["precipitation"][index] <= (ideals["precip"]+6)):
            score += 2
        elif (weatherData["precipitation"][index] <= (ideals["precip"]+8)):
            score += 1

        #
        if (weatherData["relativehumidity_mean"][index] <= (ideals["humidity"])):
            score += 5
        elif (weatherData["relativehumidity_mean"][index] <= (ideals["humidity"]+20)):
            score += 4
        elif (weatherData["relativehumidity_mean"][index] <= (ideals["humidity"]+40)):
            score += 3
        elif (weatherData["relativehumidity_mean"][index] <= (ideals["humidity"]+60)):
            score += 2
        elif (weatherData["relativehumidity_mean"][index] <= (ideals["humidity"]+80)):
            score += 1

        # TODO account for wind speed and direction too

        scoreList.append(score)

    return scoreList
