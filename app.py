from flask import Flask, jsonify, request
import utils
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

    crags = utils.getAndFilterCrags(lat, lon, radius, style)
    cragsWithWeather = utils.addWeatherToCrags(crags)
    return jsonify(crags)

if __name__ == '__main__':
    app.run()