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
        self.client_sock_mapping = dict()
        self.client = None
        self.connected = False
        self.subscribers = []
        self.client_id_client_mapping = dict()
 
    def on_connect(self, client, userdata, flags, rc):
        print('Connected')
        self.connected = True
        client.subscribe(userdata['topic'])
        self.subscribers.append(client)
        print('Subscribing to topic:', userdata['topic'])
    
    def on_socket_open(self, client, userdata, sock):
        print('Socket Opened for subscriber', sock._socket.fileno())
        self.client_sock_mapping[sock._socket.fileno()] = client
        self.inputs.append(sock._socket.fileno())

    def on_socket_close(self, client, userdata, sock):
        print('Socket Closed for subscriber', sock._socket.fileno())
        del self.client_sock_mapping[sock._socket.fileno()]
        self.inputs.remove(sock._socket.fileno())

    def on_message(self, client, userdata, msg):
        userdata['callback'](userdata['client_id'], msg.topic, msg.payload)

    def keep_alive(self, msg, topic = 'dummy'):
        for subscriber in self.subscribers:
            subscriber.publish(topic, msg)
        

    def add_client(self, callback, client_id, client_group='Default', topic='90113Keerthu', broker_addr='broker.emqx.io', broker_port=8083, keep_alive=60):
        # TODO - Make this thread safe and interrupt the select
        client = mqtt.Client(client_id=client_id, transport='websockets',userdata={'client_id': client_id, 'client_group':client_group, 'callback':callback, 'topic': topic})
        client.on_connect = self.on_connect
        client.on_socket_open = self.on_socket_open
        client.on_socket_close = self.on_socket_close
        client.on_message = self.on_message
        client.connect(broker_addr, broker_port, keep_alive)
        self.client_id_client_mapping[client_id]=client

    def wait_for_messages(self):
        try:
            readable, writable, exceptional = select(self.inputs, self.outputs, self.inputs)
            print('Out of the select loop', readable, writable, exceptional)
            if len(readable) > 0:
                for read_item in readable:
                    if read_item in self.client_sock_mapping:
                        print('Handling socket', read_item)
                        my_client = self.client_sock_mapping[read_item]
                        print('Using client',  my_client)
                        my_client.loop()
        except:
            #print('Exception Occurred')
            pass

    def pub_on_connect(self, client, userdata, flags, rc):
        print('Publisher connected')
        self.connected = rc == 0
        self.connect_callback(self.connected)
        #client.subscribe(userdata['topic'])
        print('Callback called')

    def pub_on_socket_open(self, client, userdata, sock):
        print('Socket Opened for publisher', sock._socket.fileno())
        self.client_sock_mapping[sock._socket.fileno()] = client
        self.inputs.append(sock._socket.fileno())
        
    def pub_on_socket_close(self, client, userdata, sock):
        print('Socket Closed for publisher', sock._socket.fileno())
        del self.client_sock_mapping[sock._socket.fileno()]
        self.inputs.remove(sock._socket.fileno())

    def set_publisher(self, connect_callback, client_id, client_group='Default', topic='90113Keerthu', broker_addr='broker.emqx.io', broker_port=8083, keep_alive=60):
        client = mqtt.Client(client_id=client_id, transport='websockets',userdata={'client_id': client_id, 'client_group':client_group, 'topic': topic})
        client.on_connect = self.pub_on_connect
        client.on_socket_open = self.pub_on_socket_open
        client.on_socket_close = self.pub_on_socket_close
        self.topic = topic
        self.connect_callback = connect_callback
        client.connect(broker_addr, broker_port, keep_alive)
        self.client = client

    def publish(self, msg):
        print('Publishing message in client')
        if self.client != None:
            print('Sending messsage: ', msg, ' on topic: ', self.topic)
            self.client.publish(self.topic, msg)

if __name__ == '__main__':
    my_manager = MqttManager()
    my_manager.add_client(test_callback,'90113Ke','Default','dev_man_virt')
    

    while True: 
        my_manager.wait_for_messages()


