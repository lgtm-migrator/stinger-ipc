"""
DO NOT MODIFY THIS FILE.  It is automatically generated and changes will be over-written
on the next generation.

This is the Server for the SignalOnly interface.
"""

import json
from connection import MqttConnection


class SignalOnlyServer(object):

    def __init__(self, connection: MqttConnection):
        self._conn = connection
        
    
    def emit_anotherSignal(self, one: float, two: bool, three: str):
        payload = {
            "one": one, 
            "two": two, 
            "three": three, 
        }
        self._conn.publish("SignalOnly/signal/anotherSignal", json.dumps(payload), qos=1, retain=False)

    

    

if __name__ == '__main__':
    """
    This shows an example on how to run the code.  Ideally, your app should do something similar, but use the methods in
    a more meaningful way.
    """
    from time import sleep

    conn = MqttConnection('localhost', 1883)
    server = SignalOnlyServer(conn)

    server.emit_anotherSignal(1.0, True, "Joe")
    

    sleep(4)

    server.emit_anotherSignal(one=1.0, two=True, three="Joe")
    