from flask import Flask
from threading import Thread
from waitress import serve

app = Flask('')


@app.route('/')
def home():
    return "Bot is online!"


def run():
    # production server using waitress
    serve(app, host="0.0.0.0", port=8082)


def start_server():
    t = Thread(target=run)
    t.start()
