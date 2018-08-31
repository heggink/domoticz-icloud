"""
<plugin key="AppleDevices" name="Apple iCloud Device Presence" author="heggink" version="0.0.2">
    <params>
        <param field="Username" label="Apple user name" width="150px" required="true" default="username"/>
        <param field="Password" label="Apple Password" width="150px" required="true" default="password"/>
        <param field="Mode1" label="Apple device name" width="150px" required="true" default="device"/>
        <param field="Mode2" label="Poll period (s)" width="150px" required="true" default="30"/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="true" />
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz
#import datetime

from pyicloud import PyiCloudService
from geopy.distance import vincenty
import time

#v0.0.1:

class BasePlugin:

    def __init__(self):
        self.deviceName = ' '
        self.username = ''
        self.password = ''
        self.id = ''
        self.pollPeriod = 0
        self.pollCount = 0
        self.home = (0, 0)
        self.circleLatitude = 0
        self.circleLongitude = 0
        self.away = (1, 1)
        self.mindist = 0.1
        self.lastloc = 0
        self.lastdist = 100000000
        self.difdist = 0
        self.count = 0
        return

    def onStart(self):
        Domoticz.Log("onStart called")

        if (Parameters["Mode6"] == "Debug"):
            Domoticz.Debugging(1)
            Domoticz.Debug('devicename established: '+ self.deviceName)

        self.deviceName = Parameters["Mode1"]

        if ("iCloud" not in Images):
            Domoticz.Debug('Icons Created...')
            Domoticz.Image('iCloud.zip').Create()
            iconPID = Images["iCloud"].ID

        self.username=Parameters["Username"]
        self.password=Parameters["Password"]

        # Get the location from the Settings
        if not "Location" in Settings:
            Domoticz.Log("Location not set in Preferences")
            return False
        
        # The location is stored in a string in the Settings
        loc = Settings["Location"].split(";")
        self.home = (float(loc[0]), float(loc[1]))
        Domoticz.Debug("Coordinates from Domoticz: " + str(loc[0]) + ";" + str(loc[1]))

        if loc == None or loc[0] == None:
            Domoticz.Log("Unable to parse coordinates")
            return False

#
#	initialise the icloud service and create device if icloud knows it
#
        api = PyiCloudService(self.username, self.password)
        if api == None:
            Domoticz.Log('Error Authenticating iCloud or Connection Problem...')
            Domoticz.Log('Please Use Correct Credentials and Restart The Plugin!')

        else:
            for rdev in api.devices:
                dev = str(rdev)
                Domoticz.Debug('Iterating device: [' + dev + ']' + ' to find [' + self.deviceName + ']')
                if self.deviceName in dev:
                        if 1 and 2 not in Devices:
                                Domoticz.Debug(dev + ' matches ' + self.deviceName)
                                Domoticz.Device(Name='GFC', Unit=1, TypeName="Switch", Image=iconPID, Used=1).Create()
                                Domoticz.Device(Name='Distance', Unit=2, TypeName="Distance", Used=1).Create()
                                Domoticz.Debug(str(self.deviceName))
                                Domoticz.Debug("Devices created.")

        self.pollPeriod = int(int(Parameters["Mode2"]) / 10)
        self.pollCount = self.pollPeriod - 1
        Domoticz.Debug('PollPeriod: ' + str(self.pollPeriod))
        Domoticz.Debug('PollCount: ' + str(self.pollCount))
        Domoticz.Heartbeat(10)

    def onStop(self):
        Domoticz.Log("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called")

    def onMessage(self, Connection, Data, Status, Extra):
        Domoticz.Log("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        Command = Command.strip()
        action, sep, params = Command.partition(' ')
        action = action.capitalize()
        params = params.capitalize()
 
        if Command=='Off':
            UpdateDevice(Unit,0,'Off')
        elif Command=='On':
            UpdateDevice(Unit,1,'On')

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Debug("onHeartBeat called:"+str(self.pollCount)+"/"+str(self.pollPeriod))
        if self.pollCount >= self.pollPeriod:
            Domoticz.Debug("Checking iCloud...")
            api = PyiCloudService(self.username, self.password)
            for rdev in api.devices:
                dev = str(rdev)
                Domoticz.Debug('Iterating device: [' + dev + ']' + ' to find [' + self.deviceName + ']')
                if self.deviceName == dev:
                    curr_loc = rdev.location()
                    if curr_loc is None:
                        Domoticz.log('Unable to find location for ' + dev)
                        dist = vincenty(self.home,away).miles

                    else:
                        latitude = float(curr_loc['latitude'])
                        longitude = float(curr_loc['longitude'])
                        current = (latitude,longitude)
                        dist = vincenty(self.home,current).miles
                        self.difdist = abs(dist - self.lastdist)
                        self.count = self.count + 1
#                       Domoticz.Debug('I got location for ' + self.deviceName + ' of lat: ' + current['latitude'] + ', long: ' + ', ' + current['longitude'] + ' Finished: ' + str(curr_loc['locationFinished']) + ', Distance: ' + str(dist) + ' miles')
                        Domoticz.Debug('I got location for ' + self.deviceName + ' of lat: ' + str(latitude) + ', long: ' + ', ' + str(longitude) + ' Finished: ' + str(curr_loc['locationFinished']) + ', Distance: ' + str(dist) + ' miles')

                        if self.lastdist == 100000000:
                            Domoticz.Debug('Starting up so update location')
#			    FIRST TIME WE ARE CALLED, ALWAYS UPDATE
#                            updatedomo(dist)
                            Domoticz.Debug('Update dist: ' + str(self.difdist))
                            UpdateDevice(2,1, str( dist * 1609))
                            if dist <= self.mindist:
                                Domoticz.Debug('Switching device ON: ' + self.deviceName)
                                UpdateDevice(1,1,'On')
                            else:
                                if (self.lastdist > self.mindist) and (self.lastdist != 100000000):
                                    Domoticz.Debug('Device OFF but already reported OFF so no action: ' + self.deviceName)
                                else:
                                    Domoticz.Debug('Switching device OFF: ' + self.deviceName)
                                    UpdateDevice(1,0,'Off')

                            self.lastdist = dist
                            continue

                        if self.count == 120:
                            Domoticz.Debug('Counter hit, update location')
#			    EVERY 120 CYCLES, FORCE UPDATE AND RESET COUNTER
                            self.count = 0
#                            updatedomo(dist)
                            Domoticz.Debug('Update dist: ' + str(self.difdist))
                            UpdateDevice(2,1, str( dist * 1609))
                            if dist <= self.mindist:
                                Domoticz.Debug('Switching device ON: ' + self.deviceName)
                                UpdateDevice(1,1,'On')
                            else:
                                if (self.lastdist > self.mindist) and (self.lastdist != 100000000):
                                    Domoticz.Debug('Device OFF but already reported OFF so no action: ' + self.deviceName)
                                else:
                                    Domoticz.Debug('Switching device OFF: ' + self.deviceName)
                                    UpdateDevice(1,0,'Off')

                            lastdist = dist
                            continue

                        if self.difdist > self.mindist:
#			    we should update but check for anomalies
                            Domoticz.Debug('Difdist > mindist, update location')
#                            updatedomo(dist)
                            Domoticz.Debug('Update dist: ' + str(self.difdist))
                            UpdateDevice(2,1, str( dist * 1609))
                            if dist <= self.mindist:
                                Domoticz.Debug('Switching device ON: ' + self.deviceName)
                                UpdateDevice(1,1,'On')
                            else:
                                if (self.lastdist > self.mindist) and (self.lastdist != 100000000):
                                    Domoticz.Debug('Device OFF but already reported OFF so no action: ' + self.deviceName)
                                else:
                                    Domoticz.Debug('Switching device OFF: ' + self.deviceName)
                                    UpdateDevice(1,0,'Off')

                            self.lastdist = dist
                            continue
  
                        else:
#			    NO UPDATE NEEDED AS DISTANCE WITHIN THE RANGE
                            Domoticz.Debug('No update needed as within last distance')

            self.pollCount = 0 #Reset Pollcount
        else:
            self.pollCount = self.pollCount + 1


global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data, Status, Extra):
    global _plugin
    _plugin.onMessage(Connection, Data, Status, Extra)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

def UpdateDevice(Unit, nValue, sValue):
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it 
    if (Unit in Devices):
        if (Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue):
            Devices[Unit].Update(nValue=nValue, sValue=str(sValue))
            Domoticz.Debug("Update "+str(nValue)+":'"+str(sValue)+"' ("+Devices[Unit].Name+")")
    return


    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return
