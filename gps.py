# This imports the time module to be used later in the script for timing purposes.
import time
import json  # This imports the json module to be used later in the script for encoding/decoding JSON data
import board  # This imports the board module from the Adafruit CircuitPython library, which provides access to low-level board information
# This imports the busio module from the Adafruit CircuitPython library, which provides access to I/O communication buses.
import busio
# This imports the MQTT client from the Paho MQTT library and renames it as "mqtt".
import paho.mqtt.client as mqtt
# This imports the Adafruit GPS library, which provides a Python interface for interacting with GPS devices.
import adafruit_gps

# This line creates a serial connection using the serial library.
import serial
# The devttyUSB0 argument specifies the device name for the connection and baudrate specifies the baud rate to be used for the connection,
# which is set to 9600. The timeout argument sets the time to wait for a response from the device before timing out, and it is set to 10 seconds.
uart = serial.Serial("devttyUSB0", baudrate=9600, timeout=10)

# This line creates a GPS object using the adafruit_gps library and the previously created serial connection.
# The debug argument is set to false, which means that debug information will not be printed.
gps = adafruit_gps.GPS(uart, debug=False)


# This is a callback function that is called when the MQTT client connects to the broker.
def on_connect(client, userdata, flags, rc):
    # The rc argument is the result code of the connection attempt, and if it is 0, the connection was successful.
    print("Connection Successful {0}".format(rc))
    # In that case, the function prints a message indicating a successful connection and then subscribes to the MQTT topic 'topic1'.
    client.subscribe('topic1')


# This is a callback function that is called when a message is received on the MQTT topic to which the client is subscribed.

def on_message(client, userdata, msg):
    # The msg argument contains the received message and its topic.
    print("Topic = {0}, msg = {1}".format(msg.topic, msg.payload))
    # If the topic of the message is 'topic1', the function prints a message indicating the received payload.
    if msg.topic == 'topic1':
        print("Incoming message{0}".format(msg.payload))


# These lines set up an MQTT client and connect it to an MQTT broker at the IP address '192.168.10.15' on port 1883.
client = mqtt.Client()
# The keepalive argument sets the time in seconds to keep the connection alive when no data is being sent.
client.connect("192.168.10.15", port=1883, keepalive=60)
# The on_connect and on_message callbacks are set to the previously defined functions.
client.on_connect = on_connect
client.on_message = on_message

# Turn on the basic GGA and RMC info (what you typically want)

# type of information
gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
# the rate at which this information should be sent.
gps.send_command(b'PMTK220,1000')

# This line sets the last_print variable to the current monotonic time.
last_print = time.monotonic()

while True:
    gps.update()
    current = time.monotonic()
    # This line checks if one second has elapsed since the last time the GPS data was printed.
    # If it has been at least one second, the code inside the if block will execute.
    if current - last_print >= 1.0:
        last_print = current
        # This block checks if the gps object has a GPS fix.
        # If the gps object has a fix, the code inside the if block will execute.

        if not gps.has_fix:
            print("Waiting for fix...")
            continue
        # We have a fix! (gps.has_fix is true)
        # Publish the GPS data as a message to the MQTT topic
        latitude = gps.latitude
        longitude = gps.longitude
        fix_quality = gps.fix_quality
        data = {
            "latitude": latitude,
            "longitude": longitude,
            "fix_quality": fix_quality
        }
        # creates a Python dictionary object called data containing the GPS data
        payload = json.dumps(data)
        client.publish("topic1", payload)
    client.loop()
    ''' This line calls the loop method of the client object, which handles network communication and message handling for the MQTT client.
    This line must be called regularly to keep the client running and processing incoming messages'''
