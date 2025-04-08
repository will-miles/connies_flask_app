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
    long = request.args.get('long')
    radius = request.args.get('radius')
    style = request.args.get('style')
    print(style)
    allCrags = aws_controller.get_crags(style)
    deserializedData = utils.deserialize(allCrags)

    matchingCrags = deserializedData['Items']
    return jsonify(deserializedData)


if __name__ == '__main__':
    app.run()