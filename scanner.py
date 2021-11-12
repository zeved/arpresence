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

from raw_packet.Scanners.arp_scanner import ArpScan
from typing import List, Dict, Union
from prettytable import PrettyTable
from datetime import datetime
import json


class Scanner:
  def __init__(self, config, base):
    self.config = config
    self.base = base
    self.mode = self.config['mode']

  def scan(
      self,
      interface: Union[None, str] = None,
      timeout: int = 5,
      retry: int = 5,
      mqtt_client = None,
  ):

    self.base.print_info('[scanner]: starting')

    try:
      net_interface = str = \
        self.base.network_interface_selection(
          interface_name=interface,
          message='Please select a network interface'
        )

      net_interface_settings: Dict[str, Union[None, str, List[str]]] = \
        self.base.get_interface_settings(
          interface_name = net_interface,
          required_parameters = [
            'mac-address',
            'ipv4-address',
            'first-ipv4-address',
            'last-ipv4-address',
          ]
        )

      self.base.print_info(f'[scanner]: interface -> %s' % net_interface_settings['network-interface'])
      self.base.print_info(f'[scanner]: this IP -> %s' % net_interface_settings['ipv4-address'])
      self.base.print_info(f'[scanner]: this MAC -> %s' % net_interface_settings['mac-address'])

      arp_scanner: ArpScan = ArpScan(network_interface = net_interface)
      results: List[Dict[str, str]] = arp_scanner.scan(
        timeout,
        retry,
        target_ip_address = None,
        check_vendor = True,
        exclude_ip_addresses = net_interface_settings['ipv4-address'],
        exit_on_failure = True,
        show_scan_percentage = True,
      )

      assert len(results) != 0, 'no devices found'

      if (self.mode == 'all'):
        pretty_table = PrettyTable([
          self.base.cINFO + 'IP' + self.base.cEND,
          self.base.cINFO + 'MAC' + self.base.cEND,
          self.base.cINFO + 'vendor' + self.base.cEND
        ])

        self.base.print_info('[scanner]: found devices: ')
        for result in results:
          device = {
            'mac': result['mac-address'],
            'ip': result['ip-address'],
            'vendor': result['vendor'],
          }

          pretty_table.add_row([
            device['ip'],
            device['mac'],
            device['vendor']
          ])

        print(pretty_table)

        if (mqtt_client is not None):
          self.base.print_info('[scanner]: sending presence data to MQTT broker...')

          for device in results:
            payload = {
              'ip': device['ip-address'],
              'mac': device['mac-address'],
              'vendor': device['vendor'],
              'last_seen': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            mqtt_client.client.loop()
            mqtt_client.send(json.dumps(payload))
        else:
          self.base.print_warning('[scanner]: no MQTT client; won\'t report anything')

      elif (self.mode == 'targets'):
        pretty_table = PrettyTable([
          self.base.cINFO + 'IP' + self.base.cEND,
          self.base.cINFO + 'MAC' + self.base.cEND,
          self.base.cINFO + 'vendor' + self.base.cEND,
          self.base.cINFO + 'name' + self.base.cEND
        ])

        targets = list(
          map(
            lambda target: {
              'mac': target['mac'],
              'name': target['identifier'],
            },
            self.config['targets']
          )
        )

        found_targets = []

        if (len(results) < 1):
          self.base.print_warning('[scanner]: no devices found')
          return

        for result in results:
          found_target = [ \
            target for target in targets if target['mac'] == result['mac-address']
          ]

          if (len(found_target) > 0):
            found_target = \
              {
                'mac': result['mac-address'],
                'name': found_target[0]['name'],
                'ip': result['ip-address'],
                'vendor': result['vendor'],
              }
            found_targets.append(found_target)

            pretty_table.add_row(
              [
                found_target['ip'],
                found_target['mac'],
                found_target['vendor'],
                found_target['name']
              ]
            )

        if (len(found_targets) > 0):
          self.base.print_info('[scanner]: targets found: ')
          print(pretty_table)

          if (mqtt_client is not None):
            self.base.print_info('[scanner]: sending presence data to MQTT broker...')

            for target in found_targets:
              payload = {
                'name': target['name'],
                'ip': target['ip'],
                'mac': target['mac'],
                'vendor': target['vendor'],
                'last_seen': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
              }
              mqtt_client.client.loop()
              mqtt_client.send(json.dumps(payload))
          else:
            self.base.print_warning('[scanner]: no MQTT client; won\'t report anything')
        else:
          self.base.print_warning('[scanner]: no targets found')

    except Exception as e:
      self.base.print_error(f'[scanner]: exception -> %s' % e)
