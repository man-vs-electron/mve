from __future__ import print_function

import paho.mqtt.client as paho
import mve.udp
import mve.utils
import time
import json


def always_true(topic, payload):
    return True

def print_message(topic, payload):
    print("MQTT Message: %s - %s" % (topic, payload))

_default_callback_list = [(always_true, print_message)]

class Client(object):

    def __init__(self, client_name, subscriptions = [], callback_list = _default_callback_list, first_only = True, verbose=True):
        """Create a new mqtt client
        
        This convenience class wraps up desired supscriptions and 
        how to handle messages.  It auto-discovers where the hub is
        using UDP multicast.  See the mve.udp for more info.

        Arguments
        =========
        client_name - a string identifying the client
        subscriptions - a list of strings, each of which is a
              proper mqtt message subscription.
        callback_list - a list of tuples.  Each tuple has two items.
              The first item is a lambda expression that takes a topic
              and a payload, returning True or False.  For each message
              received, it this expression returns true, it calls the 
              second item in the tuple, passing the topic and payload.
        first_only - If true, it quits working through the callback_list 
              when it hits the first true.  Otherwise it will always check
              all everything on the callback_list
        verbose - If true, print out error messages.
        """
        response, hub_ip = mve.udp.register(client_name)
        self.verbose=verbose
        self.first_only = first_only
        if verbose:
            print("Foud Hub.  IP is: %s" % hub_ip)
        self.subscriptions = subscriptions
        self.callback_list = callback_list
        self.client_name = client_name
        self.hub_ip = hub_ip

    def on_connect(self, client, userdata, flags, rc):
        """Subscribes to everything passed in via subscriptions
        """
        for subscription in self.subscriptions:
            if self.verbose:
                print("Subscribing to %s" % subscription)
            client.subscribe(subscription)

    def on_message(self, client, userdata, message):
        """Check the callbacks when a message is received

        The payloads will be decoded using json.
        """
        topic = message.topic
        try:
            payload = None if message.payload is None else json.loads(message.payload)
        except:
            payload = str(message.payload)
            #mve.utils.eprint("Error decoding payload as JSON. Skipping message.  Topic=%s, Payload=%s" % (topic, str(message.payload)))

        for criteria, callback in self.callback_list:
            if criteria(topic, payload):
                callback(topic, payload)
                if self.first_only:
                    return
            
    def connect(self):
        """Connect to the server.

        It will have been discovered via UPD using the
        constructor.
        """
        self.client = paho.Client(self.client_name)
        self.client.on_connect=self.on_connect
        self.client.on_message = self.on_message
        resp = self.client.connect(self.hub_ip)
        if resp == paho.CONNACK_ACCEPTED:
            if self.verbose:
                print("Connection succeeded")
            self.client.loop_start()
            return True
        else:
            if self.verbose:
                print("Connection failed: %d" % resp)
            return False

    def connect_stubborn(self):
        """Keep trying to connect until successful.

        If connecting fails, sleep for one second and
        then try again.  Useful if recovering from
        a power outage and the client starts before the
        server.
        """
        if self.verbose:
            print("Connecting")
        while not self.connect():
            if self.verbose:
                print('.', end='')
            time.sleep(1)
        if self.verbose:
            print("Connected")

    def disconnect(self):
        """Disconnect and stop the processing loop
        """
        self.client.disconnect()
        self.client.loop_stop()

    def publish(self, topic, payload, retain=False, json_payload=True):
        """Publish some payload to a topic.

        The payload will be encoded using json.

        Arguments
        =========
        topic - the topic to publish
        payload - the payload to publish.  Will be dumped to json
        retain - whether to mark the MQTT message as retain
        """
        self.client.publish(topic, json.dumps(payload) if json_payload else str(payload), retain=retain)
