from flask import Flask, jsonify, request, abort
import utils
import aws_controller
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app, resources={r"/get-crags": {"origins": "localhost:3000"}})
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/')
def index():
    return "This is the main page."

# 127.0.0.1:5000/get-crags?style=winter&radius=50&lat=53.52574940018496&long=-1.919685834247175
@app.route('/get-crags')
@cross_origin(origin='localhost:3000',headers=['Content-Type','Authorization'])
def get_crags():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    radius = request.args.get('radius')
    style = request.args.get('style')
    trueApiKey = aws_controller.get_secret('/get-crags')['GET_CRAGS_API_KEY']
    requestApiKey = request.args.get('api_key')

    if requestApiKey != trueApiKey:
        return abort(403)

    crags = utils.getAndFilterCrags(lat, lon, radius, style)
    utils.addWeatherToCrags(crags)
    for crag in crags:
        crag["weather_score"] = utils.calculateWeatherScore(crag)
    return jsonify(crags)

if __name__ == '__main__':
    app.run()