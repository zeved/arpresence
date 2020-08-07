#
#  Copyright (c) 2020 Zevedei Ionut
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import paho.mqtt.client as mqtt

class MQTTClient:
  def __init__(self, broker_ip, broker_port, user, password):
    self.broker_ip = broker_ip
    self.broker_port = broker_port
    self.user = user
    self.password = password
    self.client = mqtt.Client()
    
  def on_connect(self, client, data, flags, code):
    print('[mqtt]: connected')
  
  def on_message(self, data, message):
    print(f'[mqtt]: topic %s -> %s' % (message.topic, message.payload))
    
  def on_disconnect(self):
    print('[mqtt]: disconnected')
    self.client.connect(self.broker_ip, self.broker_port)
    
  def send(self, message):
    # add sending
    
  def connect(self):
    self.client.on_connect = self.on_connect
    self.client.on_message = self.on_message
    self.client.on_disconnect = self.on_disconnect
    self.client.connect(self.broker_ip, self.broker_port)
    self.client.loop_forever()