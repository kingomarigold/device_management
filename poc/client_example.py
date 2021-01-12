import paho.mqtt.client as mqtt
import select

inputs = []
outputs = []

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    print('User Data is', userdata)

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

def on_socket_open(client, userdata, sock):
    print('Socket Opened: ',sock._socket.fileno())
    print(dir(sock._socket))
    inputs.append(sock._socket.fileno())

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    #pass

client = mqtt.Client(client_id='90113Ke',transport='websockets',userdata={'client_id':'90113Ke'})
client.on_connect = on_connect
client.on_message = on_message
client.on_socket_open = on_socket_open

client.connect("test.mosquitto.org", 8080, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
#client.loop_forever()

while True:
    readable, writable, exceptional = select.select(inputs, outputs, inputs)
    print('Readble: ', readable)
    client.loop()
    
