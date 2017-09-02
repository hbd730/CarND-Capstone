#!/usr/bin/env python

import socketio
import eventlet
import eventlet.wsgi
import time
from flask import Flask, render_template

from bridge import Bridge
from conf import conf

# Made some changes to decrease amount of data sent between ROS and simulator as suggested by
# https://github.com/amakurin/CarND-Capstone/commit/9809bc60d51c06174f8c8bfe6c40c88ec1c39d50

sio = socketio.Server()
app = Flask(__name__)
bridge = Bridge(conf)

# msgs = []
msgs = {}


@sio.on('connect')
def connect(sid, environ):
    print("connect ", sid)
    bridge.publish_dbw_status(True)


def send(topic, data):
    #msgs.append((topic, data))
    msgs[topic] = data

bridge.register_server(send)


@sio.on('telemetry')
def telemetry(sid, data):
    bridge.publish_odometry(data)
    for i in range(len(msgs)):
        # topic, data = msgs.pop(0)
        topic, data = msgs.popitem()

        sio.emit(topic, data=data, skip_sid=True)


@sio.on('control')
def control(sid, data):
    bridge.publish_controls(data)


@sio.on('obstacle')
def obstacle(sid, data):
    bridge.publish_obstacles(data)


@sio.on('lidar')
def obstacle(sid, data):
    bridge.publish_lidar(data)


@sio.on('trafficlights')
def trafficlights(sid, data):
    bridge.publish_traffic(data)


@sio.on('image')
def image(sid, data):
    bridge.publish_camera(data)

if __name__ == '__main__':

    # wrap Flask application with engineio's middleware
    app = socketio.Middleware(sio, app)

    # deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(('', 4567)), app)
