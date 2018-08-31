# domoticz-icloud
iCloud device location python plugin for Domoticz
This plugin requires installation of pyicloud and geopy to work

Create a hardware device per iCloud device to be monitored 

Ensure that the devices are listed under Friends in your iCloud account

## NOT TESTED FOR 2FA although pyicloud supposedly supports it

## Parameters
| Parameter | Description |
| :--- | :--- |
| **Apple user name** | User name for the apple account |
| **Apple user password** | Password for the apple account |
| **Apple device name** | Device name to be tracked |
| **Poll period in seconds** | Polling time in seconds to check for the device location |
## Devices
| Name | Description |
| :--- | :--- |
| **On/Off device** | Depending on whether the iCloud device is at the domoticz location (coordinates specied in the domoticz settings) |
| **Distance device** | with the geographical distance from the device to domoticz (in cm) |

## To do
