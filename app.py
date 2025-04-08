from flask import Flask, jsonify, request
import aws_controller
import utils

app = Flask(__name__)

@app.route('/')
def index():
    return "This is the main page."

@app.route('/get-crags')
def get_crags():
    lat = request.args.get('lat')
    lon = request.args.get('long')
    radius = request.args.get('radius')
    style = request.args.get('style')
    print(style)
    allCrags = aws_controller.get_crags(style)
    deserializedData = utils.deserialize(allCrags)

    matchingCrags = deserializedData['Items']

    # 127.0.0.1:5000/get-crags?style=winter&radius=50&lat=53.52574940018496&long=-1.919685834247175

    def check_distance(crag):
        distance = utils.getDistanceFromLatLonInKm(float(lat), float(lon), float(crag['lat']), float(crag['long']))
        print(distance, int(radius))

        if distance < int(radius):
            crag['distance'] = int(distance)
            return True
        return False

    valid_crags_iterator = filter(check_distance, matchingCrags)

    valid_crags = list(valid_crags_iterator)

    return jsonify(valid_crags)

if __name__ == '__main__':
    app.run()