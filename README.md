## ARPresence

Scans the interface for the specified MAC addresses and reports if they were found to a MQTT broker (for now)

## Config file

```
en1
192.168.0.1,1884
user,pass
c0:ff:ee:ad:d1:c4,coffee addict
```

## TODO

- implement the looping system that will continuously scan for the targets
- send data to MQTT broker when target is found on the network
- accept MQTT broker commands to add / remove targets?
- send last seen timestamp?
