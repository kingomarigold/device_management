from mqtt_manager import MqttManager
import time
import json

def callback(success):
    print('Connected success: ', success)

def do_publish():
    my_publisher = MqttManager()
    my_publisher.set_publisher(callback, 'KethuraiKeerthu', 'Default', 'dev_man_virt')
    index = 1
    msg_type = 'c'
    while True:
        time.sleep(5)
        my_publisher.publish(json.dumps({'msg':'Keethu will walk to Kethurai ' + str(index), 'client_id': '1', 'msg_type':msg_type}))
        msg_type='ka'
        index = index + 1


if __name__ == '__main__':
    do_publish()
