import network
import json
from machine import Pin
import uwebsockets.client
import os
import time
import socket

url = 'ws://185.58.207.148:8888/controller'

def do_connect():
    global sta_if
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('4elabn', 'nogivjopu')
        while not sta_if.isconnected():
            pass
        print('network config:', sta_if.ifconfig())

def auth_socket(url):
    websocket = uwebsockets.client.connect(url)
    aut_data = json.dumps({'client_id': '321'})
    websocket.send(aut_data)
    response = wait_response(websocket)
    if response == 'You are autorizated':
        return websocket
    return False

def wait_response(websocket):
    return websocket.recv()

def check_websocket(websocket):
    if not websocket.open:
        return auth_socket(url)
    return websocket

def execute_command(command):
    global pin_enable
    lampa_state = not bool(pin_enable.value())
    com = command['command']
    if com == 'enable':
        try:
            value = bool(command['value'])
        except ValueError:
            print('enable error')
            return False
        if value != lampa_state:
            pin_enable.value(lampa_state)

sta_if = network.WLAN(network.STA_IF)
do_connect()
websocket = auth_socket(url)

#pin_enable = Pin(4, Pin.OUT)
pin_enable = Pin(2, Pin.OUT)
pin_enable.value(1)

while(True):
    do_connect()
    websocket = check_websocket(websocket)
    if websocket == False:
        continue
    try:
        response = wait_response(websocket)
        command = json.loads(response)
    except ValueError:
        continue
    print(command)
    execute_command(command)
    print('Cycle')
