from mqtt_pub_sub import MqttManager
import _thread
import schedule
import time
import json
from file_handler import create_dir, write_in_chunks, merge_chunks
import traceback
import marshal
import zlib

class DeviceManager:
    def __init__(self):
        self.mqtt_manager = MqttManager()
        self.file_callback = None

    def set_file_callback(self, file_callback):
        self.file_callback = file_callback

    def do_ping(self):
        self.mqtt_manager.publish(self.default_topic, json.dumps({'msg_type': 'ka', 'client_id': self.client_id}))
    
    def thr_run(self, thr_id, id):
        while True:
            schedule.run_pending()
            time.sleep(30)

    def message_waiter(self, thr_id, id):
        while True:
            self.mqtt_manager.wait_for_messages()

    def create_scheduler(self):
        schedule.every(1).minutes.do(self.do_ping)
        _thread.start_new_thread(self.thr_run, ('Scheduler Thread',1))
        _thread.start_new_thread(self.message_waiter, ('Message Waiter Thread',2))

    def message_received(self, client_id, topic, data):
        payload = ''
        if topic.endswith('filechannel'):
            payload = marshal.loads(zlib.decompress(data))
        else:
            payload = json.loads(data)
        msg_type = payload['msg_type']
        print('Received message with type: ', msg_type)
        if msg_type == 'fb':
            self.handle_file_start(payload['name'])
        elif msg_type == 'c':
            self.handle_chunk(payload)
        elif msg_type == 'fe':
            self.handle_file_end(payload['name'], payload['tc'])

    def handle_file_start(self, name):
        print('Handling file start for file: ', name)
        try:
            create_dir(name)
        except:
            print('Exception in creating directory', traceback.format_exc())
        print('Created directory')

    def handle_chunk(self, payload):
        try:
            if write_in_chunks(payload['name'], payload['ci'], payload) == True:
                print('Successful in writing chunk with index: ', payload['ci'], ' for file: ', payload['name'])
            else:
                print('Not successful in writing chunk with index: ', payload['ci'], ' for file: ', payload['name'])
        except:
            print('Exception in handling chunk', traceback.format_exc())

    def handle_file_end(self, name, total_chunks):
        try:
            if merge_chunks(name, total_chunks) == True:
                print('Merged file with name: ', name)
                if self.file_callback != None:
                    self.file_callback(name)
            else:
                print('Could not merge file with name: ', name)
        except:
            print('Exception in handling file end', traceback.format_exc())

    def connect_callback(self):
        print('Inside callback for client')
        self.send_message(json.dumps({'msg_type': 'c', 'client_id': self.client_id}))

    def connect(self, client_id, client_group = 'Default', default_topic = 'dev_man_virt',broker_addr='broker.emqx.io', broker_port=8083, keep_alive=120):
        self.client_id = client_id
        self.client_group = client_group
        self.default_topic = default_topic
        self.mqtt_manager.connect(self.message_received, client_id, client_group, [(client_id + '_channel', 1), (client_id + '_filechannel',1), (client_group + '_filechannel',1),(client_group + '_channel', 1), (default_topic +'_channel', 1)], broker_addr, broker_port, keep_alive, self.connect_callback)
        self.create_scheduler()

    def send_message(self, msg):
        print('Sending message')
        self.mqtt_manager.publish(self.default_topic,msg)
        print('Sent message')


if __name__ == '__main__':
    device_manager = DeviceManager()
    device_manager.connect('90113Keerthu')

    while True:
        time.sleep(30)


