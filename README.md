## ARPresence

Scans the interface for the specified MAC addresses and reports if they were found to a MQTT broker (for now)

## Config file

```json
{
  "interface": "en0",
  "mode": "targets|all",
  "interval": 10,
  "mqtt": {
    "ip": "192.168.22.100",
    "port": 64888,
    "topic": "arpresence",
    "client_id": "ARPresence",
    "username": "user",
    "password": "password"
  },
  "targets": [
    {
      "mac": "c0:ff:ee:ad:d1:c4",
      "identifier": "coffee addict"
    }
  ]
}
```

## TODO

- ~~send data to MQTT broker when target is found on the network~~ DONE
- accept MQTT broker commands to add / remove targets?
- ~~send last seen timestamp?~~ DONE
- add possibility to POST data to a HTTP listener
- ~~add looping system and interval~~
- ~~add scanning mode all / targets~~
