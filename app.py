import imp
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS #comment this on deployment
from youtube.yt_request import send_subscriber_mail, youtube
from youtube.env_details import env_details
from youtube.api_util import get_channel_from_video

# from flask_restful import Api, Resource, reqparse
# from api.HelloApiHandler import HelloApiHandler

app = Flask(__name__, static_url_path='', static_folder='frontend/yt_watchman/build')
CORS(app) #comment this on deployment

# api = Api(app)

@app.route("/", methods=["GET"])
def serve():
    # return jsonify({"Hello": "world"})
    return send_from_directory(app.static_folder,'index.html')


@app.route("/subscribe", methods=["POST"])
def subscribe():
    tags = request.json['tags']
    video_link = request.json['video_link']

    channel_id = get_channel_from_video(youtube, video_link)

    send_subscriber_mail(youtube, channel_id, tags, env_details["SENDER_EMAIL"], env_details["SENDER_PASS"], env_details["RECEIVER_LIST"])

    return jsonify({"response": "Subscribed Successfully!"})


if(__name__ == "__main__"):
    app.run(debug=True)








# @app.route("/yt", defaults={'path':''}, methods=["GET", "POST"])
# def yt_route(path):
#     if(request.method == "POST"):
#         print(request.form)
#         return request
#     # return "hsdl"

# api.add_resource(HelloApiHandler, '/flask/hello')