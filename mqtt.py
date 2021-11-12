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
import json


class MQTTClient:
  def __init__(self, config, base):
    self.broker_ip = config['mqtt']['ip']
    self.broker_port = config['mqtt']['port']
    self.user = config['mqtt']['username']
    self.password = config['mqtt']['password']
    self.topic = config['mqtt']['topic']
    self.client = mqtt.Client(client_id=config['mqtt']['client_id'])
    self.base = base

  def on_connect(self, client, data, flags, code):
    self.base.print_info('[mqtt]: connected')
    self.client.subscribe(self.topic)
    hello_msg = {'msg': 'hello'}
    self.client.publish(self.topic, json.dumps(hello_msg))

  # def on_message(self, message):
  #   self.base.print_info(f'[mqtt]: topic %s -> %s' % (message.topic, message.payload))
  #
  def on_disconnect(self):
    self.base.print_error('[mqtt]: disconnected')
    self.client.reconnect()

  def send(self, message):
    try:
      self.base.print_info(f'[mqtt]: sending presence data: %s' % message)
      self.client.publish(self.topic, message)
    except Exception as e:
      self.base.print_error(f'[mqtt]: publish error %s' % e)

  def connect(self):
    try:
      self.client.on_connect = self.on_connect
      # self.client.on_message = self.on_message
      self.client.on_disconnect = self.on_disconnect
      self.client.username_pw_set(self.user, self.password)
      self.client.connect(self.broker_ip, self.broker_port)
      self.client.loop()
    except Exception as e:
      self.base.print_error(f'[mqtt]: exception %s' % e)