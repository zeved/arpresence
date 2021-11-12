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

from raw_packet.Utils.base import Base
import json
import time

from mqtt import MQTTClient
from scanner import Scanner

base = Base(admin_only = True, available_platforms = ['Linux', 'Darwin'])

config = {}

def read_config():
  global config
  try:
    config_file = open('config.json', 'r')
    config = json.load(config_file)

    base.print_info(
      f'[config]: will connect to MQTT broker %s:%d and will report on topic "%s"' %
      (
        config['mqtt']['ip'],
        config['mqtt']['port'],
        config['mqtt']['topic']
      )
    )

    if (len(config['targets']) > 0 and config['mode'] != 'all'):
      base.print_info('[targets]: ')

      for target in config['targets']:
        print(f'\tMAC: %s -> %s' % (target['mac'], target['identifier']))

    return len(config['targets'])

  except Exception as e:
    base.print_error(f'[read_targets]: exception -> %s' % e)
    return 0

def main():
  if (read_config() < 1):
    base.print_error('[config.json]: no targets found in config.json file')
    exit(-1)

  mqtt = MQTTClient(config, base)
  mqtt.connect()
  scanner = Scanner(config, base)

  while (True):
    scanner.scan(config['interface'], mqtt_client = mqtt)
    time.sleep(config['interval'])

if __name__ == '__main__':
  main()
