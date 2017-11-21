import logging
import datetime
from tornado import web, websocket, escape
from lib import singleton
import json
import abc

matches = [{'mobile': 123, 'controller': 321}, {'mobile': 11, 'controller': 12}]

@singleton
class ClientCollection:
    def __init__(self):
        self.mobile_collection = []
        self.controller_collection = []
    def add_mobile(self, mobile_client):
        self.mobile_collection.append(mobile_client)
        print [e.id for e in self.controller_collection]
    def add_controller(self, controller_client):
        self.controller_collection.append(controller_client)
        print [e.id for e in self.controller_collection]
    def delete_mobile(self, mobile_client):
        self.mobile_collection.remove(mobile_client)
    def delete_controller(self, controller_client):
        him_mobiles = self.find_mobiles_by_controller(controller_client)
        for mobile in him_mobiles:
            mobile.send_controller_disconnected(controller_client)
        self.controller_collection.remove(controller_client)
    def get_mobile_client(self, mobile_id):
        for client in self.mobile_collection:
            if client.id == mobile_id:
                return client
        return None
    def get_controller_client(self, controller_id):
        for client in self.controller_collection:
            if client.id == controller_id:
                return client
        return None
    def find_mobiles_by_controller(self, controller_client):
        mobiles = []
        for match in matches:
            if match['controller'] == controller_client.id:
                mobile_client = self.get_mobile_client(match['mobile'])
                if mobile_client is not None:
                    mobiles.append(mobile_client)
        return mobiles


class Client(websocket.WebSocketHandler):
    TYPE_CONTROLLER = 1
    TYPE_MOBILE = 2
    __metaclass__ = abc.ABCMeta
    def __init__(self, application, request, **kwargs):
        super(Client, self).__init__(application, request, **kwargs)
        self.id = None
        self.type = None
        self.is_authorizated = False
    def check_origin(self, origin):
        return True

    # message format {"client_id": id}
    def autorization(self, message):
        try:
            json_object = json.loads(message)
        except ValueError:
            return False
        self.id = int(json_object["client_id"])
        self.write_message('You are autorizated')
        print 'client autorized: ' + str(self.id)
        return True

    def on_message(self, message):
        if self.is_authorizated == False:
            if self.autorization(message):
                self.is_authorizated = True
        else:
            print 'executing command'
            self.execute_command(message)
        print message

    @abc.abstractmethod
    def execute_command(self, message):
        pass

class MobileClient(Client):
    def __init__(self, application, request, **kwargs):
        super(MobileClient, self).__init__(application, request, **kwargs)
        self.type = Client.TYPE_MOBILE
    def open(self):
        print 'Mobile is connected'
        ClientCollection().add_mobile(self)
    def on_close(self):
        ClientCollection().delete_mobile(self)
        print 'Good_bue mobile'
    def execute_command(self, message):
        print 'trying execute command, message: ' + str(message)
        try:
            json_object = json.loads(message)
        except ValueError:
            print 'ValueError'
            return False
        if 'command' in message:
            command = json_object["command"]
            print 'command founded: ' + str(command)
            if command == 'enable' and 'controller_id' in message:
                controller_id = json_object["controller_id"]
                value = int(json_object["value"])
                self.send_enable_command(controller_id, value)
                return True

        return False
    def send_enable_command(self, client_id, value):
        print 'sending enable'
        controller_client = ClientCollection().get_controller_client(client_id)
        if controller_client is None:
            print 'Controller not found'
            return False
        controller_client.send_enable(value)
        print 'send command: ' + str(value)
        return True
    def send_controller_disconnected(self, controller_client):
        command = {'command': 'disconnected', 'value': controller_client.id}
        self.write_message(json.dumps(command))


class ControllerClient(Client):
    def __init__(self, application, request, **kwargs):
        super(ControllerClient, self).__init__(application, request, **kwargs)
        self.type = Client.TYPE_CONTROLLER
    def open(self):
        print 'Controler is connected'
        ClientCollection().add_controller(self)
    def on_close(self):
        ClientCollection().delete_controller(self)
        print 'Good_bue controller'
    def send_enable(self, value):
        command = {'command': 'enable', 'value': bool(value)}
        print 'send enable to client:' + str(self.id)
        self.write_message(json.dumps(command))
    def execute_command(self, message):
        pass
