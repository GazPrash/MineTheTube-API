# Rest API Endpoint

from flask import Flask, jsonify, request
from flask_cors import CORS
from main import IndexElement

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return "Welcome to minethetube api.. for more info about routes and request parameters."


@app.route("/analytics/watchtime", methods=["GET"])
def watchtime():
    url_argument = request.query_string.decode()
    fire_request = IndexElement("Analytics", "Watchtime", url_argument)
    data_response = fire_request.data_point()

    return jsonify(data_response)


@app.route("/analytics/pl_statistics", methods=["GET"])
def playlist_stats():
    url_argument = request.query_string.decode()
    fire_request = IndexElement("Analytics", "PLStatistics", url_argument)
    data_response = fire_request.data_point()

    return jsonify(data_response)


@app.route("/analytics/channelstats", methods=["GET"])
def channel_stats():
    second_arg, url_argument = request.query_string.decode().split("&&")
    fire_request = IndexElement("Analytics", f"ChannelStats-{second_arg}", url_argument)
    data_response = fire_request.data_point()

    return jsonify(data_response)


@app.route(
    "/utilities/advanced_search", methods=["GET"]
)  # ?south+park&2007-5-17%2006-12-5
def advanced_search():
    parameter_string = request.query_string.decode()  # .split('&')
    # for string in parameter:
    #     string = " ".join(string.split('+'))

    fire_request = IndexElement("Utility", "AdvancedSearch", parameter_string)
    data_response = fire_request.data_point()
    return jsonify(data_response)


@app.route(
    "/utilities/pl_generator", methods=["GET"]
)  # utilities/pl_generator?key+word&limit=25
def pl_generator():
    parameter_string, max_res = request.query_string.decode().split("&limit=")

    fire_request = IndexElement(
        "Utility", "PlaylistGenerator", (parameter_string, int(max_res))
    )
    data_response = fire_request.data_point()

    return jsonify(data_response)


@app.route("/trends", methods=["GET"])
def trends():
    parameters = request.query_string.decode()
    fire_request = IndexElement("Trends", parameters, None)
    data_response = fire_request.data_point()

    return jsonify(data_response)


@app.route("/trendingtoday", methods=["GET"])
def trending_today():
    parameters = request.query_string.decode()
    fire_request = IndexElement("Trends", parameters, None)
    data_response = fire_request.data_point()

    return jsonify(data_response)


@app.route("/versus", methods=["GET"])
def versus():
    parameter_string = request.query_string.decode()

    fire_request = IndexElement("Versus", parameter_string, None)
    data_response = fire_request.data_point()

    # print(data_response, flush = True)
    return jsonify(data_response)


if __name__ == "__main__":
    app.run(debug=True)
