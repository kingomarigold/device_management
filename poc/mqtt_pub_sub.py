import paho.mqtt.client as mqtt
from select import select
import _thread
import time



def test_callback(client_id, topic, payload):
    print('Callback data: ', client_id, topic, payload)

class MqttManager:
    def __init__(self):
        self.inputs = []
        self.outputs = []
        self.client = None
        self.connected = False
        
    def on_connect(self, client, userdata, flags, rc):
        print('Connected')
        client.subscribe(userdata['topic'])
        self.connected = True
        if 'connect_callback' in userdata:
            connect_callback = userdata['connect_callback']
            if connect_callback != None:
                connect_callback()
        print('Subscribing to topic:', userdata['topic'])
    
    def on_socket_open(self, client, userdata, sock):
        print('Socket Opened for subscriber', sock._socket.fileno())
        self.inputs.append(sock._socket.fileno())

    def on_socket_close(self, client, userdata, sock):
        print('Socket Closed for subscriber', sock._socket.fileno())
        self.inputs.remove(sock._socket.fileno())

    def on_message(self, client, userdata, msg):
        userdata['callback'](userdata['client_id'], msg.topic, msg.payload)
    

    def connect(self, callback, client_id, client_group='Default', topic='90113Keerthu', broker_addr='broker.emqx.io', broker_port=8083, keep_alive=60, connect_callback=None):
        client = mqtt.Client(client_id=client_id, transport='websockets',userdata={'connect_callback': connect_callback, 'client_id': client_id, 'client_group':client_group, 'callback':callback, 'topic': topic})
        client.on_connect = self.on_connect
        client.on_socket_open = self.on_socket_open
        client.on_socket_close = self.on_socket_close
        client.on_message = self.on_message
        client.connect(broker_addr, broker_port, keep_alive)
        self.client = client
 
    def wait_for_messages(self):
        try:
            readable, writable, exceptional = select(self.inputs, self.outputs, self.inputs)
            print('Out of the select loop', readable, writable, exceptional)
            if len(readable) > 0:
                self.client.loop()
                        
        except:
            #print('Exception Occurred')
            pass


    def publish(self, topic, msg):
        print('Publishing message in client')
        if self.connected == True:
            print('Sending messsage: ', msg, ' on topic: ', topic)
            self.client.publish(topic, msg)

if __name__ == '__main__':
    my_manager = MqttManager()
    my_manager.connect(test_callback,'90113Ke','Default','dev_man_virt')
    

    while True: 
        my_manager.wait_for_messages()


