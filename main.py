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

import sys
import os

from raw_packet.Utils.base import Base
from raw_packet.Utils.utils import Utils
from raw_packet.Scanners.arp_scanner import ArpScan
from typing import List, Dict, Union
from prettytable import PrettyTable

base = Base(admin_only = True, available_platforms = ['Linux', 'Darwin'])

interface = ''
mqtt_ip = ''
mqtt_port = 1884
mqtt_user = ''
mqtt_pass = ''
targets = []

def read_config():
  global mqtt_ip, mqtt_port, mqtt_user, mqtt_pass, targets, interface
  try:
    config_file = open('config', 'r')
    config_lines = config_file.readlines()
    assert len(config_lines) != 0, 'config file is empty?'
    
    interface = config_lines[0]
    mqtt_ip = config_lines[1].split(',')[0]
    mqtt_port = int(config_lines[1].split(',')[1])
    mqtt_user = config_lines[2].split(',')[0]
    mqtt_user = config_lines[2].split(',')[1]
    targets = config_lines[3:]
    
    base.print_info(f'[config]: will connect to MQTT broker %s:%d' % (mqtt_ip, mqtt_port))
    
    if (len(targets) > 0):
      base.print_info('[targets]: ')
      
      for target in targets:
        print(f'\tMAC: %s -> %s' % (target.split(',')[0], target.split(',')[1]))
      
    return len(targets)
    
  except Exception as e:
    base.print_error(f'[read_targets]: exception -> %s' % e)
    return 0

def scan(
  interface: Union[None, str] = None,
  target_ip: Union[None, str] = None,
  timeout: int = 5,
  retry: int = 5
):
  global targets
  base.print_info('ARPresence')
  
  try:
    net_interface: str = \
      base.network_interface_selection(interface_name = interface, message = 'Please select a network interface')
    net_interface_settings: Dict[str, Union[None, str, List[str]]] = \
      base.get_interface_settings(interface_name = net_interface, required_parameters = [
        'mac-address',
        'ipv4-address',
        'first-ipv4-address',
        'last-ipv4-address',
      ])
    
    base.print_info(f'[scan]: interface -> %s' % net_interface_settings['network-interface'])
    base.print_info(f'[scan]: this IP -> %s' % net_interface_settings['ipv4-address'])
    base.print_info(f'[scan]: this MAC -> %s' % net_interface_settings['mac-address'])
    
    arp_scanner: ArpScan = ArpScan(network_interface = net_interface)
    results: List[Dict[str, str]] = arp_scanner.scan(
      timeout = timeout,
      retry = retry,
      target_ip_address = None,
      check_vendor = True,
      exclude_ip_addresses = net_interface_settings['ipv4-address'],
      exit_on_failure = False,
      show_scan_percentage = True,
    )
    
    assert len(results) != 0, 'no devices found'
    
    pretty_table = PrettyTable([
      base.cINFO + 'IP' + base.cEND,
      base.cINFO + 'MAC' + base.cEND,
      base.cINFO + 'vendor' + base.cEND,
      base.cINFO + 'name' + base.cEND,
    ])
    
    targets = list(map(lambda target: { 'mac': target.split(',')[0], 'name': target.split(',')[1]}, targets))
    found_targets = []
    
    for result in results:
      found_target = [target for target in targets if target['mac'] == result['mac-address']]
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
      base.print_info('targets found: ')
      print(pretty_table)
    else:
      base.print_warning('no targets were found')
    
  except Exception as e:
    base.print_error(f'[scan]: exception -> %s' % e)

def main():
  if (read_config() < 1):
    base.print_error('[config]: no targets found in config file')
    exit(-1)
    
  scan(interface)
  
if __name__ == '__main__':
  main()
