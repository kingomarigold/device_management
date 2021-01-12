from mqtt_pub_sub import MqttManager
import _thread
import schedule
import time
import json
import marshal
import zlib
from file_handler import read_in_chunks

class PlatformDeviceManager:

    def __init__(self):
        self.mqtt_manager = MqttManager()
        self.clients = {}

    def set_callbacks(self, device_connected, device_disconnected):
        self.device_connected = device_connected
        self.device_disconnected = device_disconnected

    def message_waiter(self, thr_id, id):
        print('Waiting for messages')
        while True:
            self.mqtt_manager.wait_for_messages()

    def monitor_clients(self, thr_id, id):
        while True:
            time.sleep(30)
            self.mqtt_manager.publish(self.default_topic + '_channel', json.dumps({'msg_type':'ka'}))
            time_threshold = time.time() - 120
            removed_clients = []
            for client_id, last_sent in self.clients.items():
                if last_sent < time_threshold:
                    removed_clients.append(client_id)
                    self.device_disconnected(client_id)
            for client_id in removed_clients:
                del self.clients[client_id]
            
        

    def message_received(self, client_id, topic, msg):
        print('Received msg: ', msg)
        my_msg = json.loads(msg)
        my_client_id = my_msg['client_id']
        if my_msg['msg_type'] == 'c':
            self.device_connected(my_client_id)
        self.clients[my_client_id] = time.time()
            

    def connect_callback(self, success):
        pass
    
    def connect(self, client_id, client_group = 'Default', default_topic = 'dev_man_virt',broker_addr='broker.emqx.io', broker_port=8083, keep_alive=60):
        self.default_topic = default_topic
        self.mqtt_manager.connect(self.message_received, client_id, client_group, default_topic, broker_addr, broker_port, keep_alive, None)
        _thread.start_new_thread(self.message_waiter, ('Message Waiter Thread',1))
        _thread.start_new_thread(self.monitor_clients, ('Client Monitor Thread',2))

    def send_file_to_client(self, client_id_or_group, file, client_file_name):
        topic =  client_id_or_group + '_filechannel'
        self.mqtt_manager.publish(topic, zlib.compress(marshal.dumps({'msg_type': 'fb', 'name':client_file_name}),9))
        with open(file, 'rb') as my_file:
            index = 0
            for chunk in read_in_chunks(my_file, 1024):
                index = index + 1
                chunk['msg_type'] = 'c'
                chunk['name'] = client_file_name
                chunk['ci'] = index
                self.mqtt_manager.publish(topic, zlib.compress(marshal.dumps(chunk), 9))
        
        self.mqtt_manager.publish(topic, zlib.compress(marshal.dumps({'msg_type': 'fe', 'name':client_file_name, 'tc': index}), 9))     


    def device_connected(self, client_id):
        print('Client : ', client_id, ' has connected')

    def device_disconnected(self, client_id):
        print('Client : ', client_id, ' has disconnected')

if __name__ == '__main__':
    platform_device_manager = PlatformDeviceManager()
    platform_device_manager.set_callbacks(platform_device_manager.device_connected, platform_device_manager.device_disconnected)
    platform_device_manager.connect('TestPlatform')

    index = 0
    while True:
        time.sleep(30)
        index = index + 1
        if index > 5:
            platform_device_manager.send_file_to_client('90113Keerthu', 'pf_3.jpg', 'pf_4.jpg')
        
        
