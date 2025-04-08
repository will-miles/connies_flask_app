from flask import Flask, jsonify, request
import utils

app = Flask(__name__)

@app.route('/')
def index():
    return "This is the main page."

# 127.0.0.1:5000/get-crags?style=winter&radius=50&lat=53.52574940018496&long=-1.919685834247175
@app.route('/get-crags')
def get_crags():
    lat = request.args.get('lat')
    lon = request.args.get('long')
    radius = request.args.get('radius')
    style = request.args.get('style')

    crags = utils.getAndFilterCrags(lat, lon, radius, style)
    cragsWithWeather = uitls.addWeatherToCrags()
    return jsonify(crags)

if __name__ == '__main__':
    app.run()