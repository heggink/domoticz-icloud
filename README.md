# domoticz-icloud
iCloud device location python plugin for Domoticz
This plugin requires installation of pyicloud and geopy to work
On invocation, it creates 2 devices:
- On/Off device depending on whether the iCloud device is at the domoticz location (coordinates specied in the domoticz settings)
- Distance device with the geographical distance from the device to domoticz (in cm)

Create a hardware device per iCloud device to be monitored 
