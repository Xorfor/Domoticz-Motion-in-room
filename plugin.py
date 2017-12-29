# Motion in Room Plugin
#
# Author: Xorfor
#
"""
<plugin key="xfr_motion" name="Motion in room" author="Xorfor" version="1.0.0">
    <params>
        <param field="Address" label="Domoticz server" width="200px" required="true" default="localhost"/>
        <param field="Port" label="Port" width="50px" required="true" default="8080"/>
        <param field="Mode1" label="IDX" width="50px" required="true"/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="true"/>
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz
import json

# custom modules
# import sys
# sys.path.append("/usr/lib/python3/dist-packages")


_HEARTBEATS = 1              # every 10 seconds

_MOTION_UNIT = 1

class BasePlugin:

    def __init__(self):
        self.__runAgain = 0
        self.__httpcon = None
        self.__counter = 0

    def onStart(self):
        # Debug
        Domoticz.Debug("onStart called")
        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)
        # Validate parameters
        # Create devices
        if _MOTION_UNIT in Devices:
            pass
        else:
            Domoticz.Device(Unit=_MOTION_UNIT, Name="Motion in room", Type=244, Subtype=73, Switchtype=8, Used=1).Create()
        # Log config
        DumpConfigToLog()
        # Connection
        self.__httpcon = Domoticz.Connection(Name="Domoticz", Transport="TCP/IP", Protocol="HTTP", Address=Parameters["Address"], Port=Parameters["Port"])
        self.__httpcon.Connect()

    def onStop(self):
        Domoticz.Debug("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")
        if Status == 0:
            url = "/json.htm?type=devices&rid=" + Parameters["Mode1"]
            Domoticz.Debug("url: " + url)
            send_data = {'Verb': 'GET',
                         'URL': url, \
                         'Headers': {'Content-Type': 'text/xml; charset=utf-8', \
                                     'Connection': 'keep-alive', \
                                     'Accept': 'Content-Type: text/html; charset=UTF-8', \
                                     'Host': Parameters["Address"] + ":" + Parameters["Port"], \
                                     'User-Agent': 'Domoticz/1.0'}
                         }
            Connection.Send(send_data)
        else:
            Domoticz.Error("Failed to connect ("+str(Status)+") to: "+Connection.Address+" with error: "+Description)

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called")
        parsed_json = json.loads(Data["Data"].decode("utf-8", "ignore"))
        switch_type = str(parsed_json["result"][0]["SwitchType"])
        status = str(parsed_json["result"][0]["Status"])
        Domoticz.Debug("SwitchType: "+switch_type)
        Domoticz.Debug("Status: "+status)
        if switch_type == "Motion Sensor":
            if status == "On":
                # Reset counter
                self.__counter = int(Parameters["Mode1"]) * 6 # 6 heartbeats in a minute

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")
        self.__runAgain -= 1
        self.__counter -= 1
        if self.__runAgain < 0:
            self.__runAgain = _HEARTBEATS
            # Execute your command
            if self.__httpcon.Connecting() or self.__httpcon.Connected():
                Domoticz.Debug("onHeartbeat called, Connection is alive.")
            else:
                self.__httpcon.Connect()
        else:
            Domoticz.Debug("onHeartbeat called, run again in "+str(self.__runAgain)+" heartbeats.")
        if self.__counter < 0:
            UpdateDevice(Unit=_MOTION_UNIT, nValue=0, sValue="Off", TimedOut=0, AlwaysUpdate=False)
            self.__counter = 0
        else:
            UpdateDevice(Unit=_MOTION_UNIT, nValue=1, sValue="On", TimedOut=0, AlwaysUpdate=False)
        Domoticz.Debug("Counter: " + str(self.__counter))


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

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

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

################################################################################
# Generic helper functions
################################################################################
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
    for x in Settings:
        Domoticz.Debug("Setting:           " + str(x) + " - " + str(Settings[x]))

def UpdateDevice(Unit, nValue, sValue, TimedOut=0, AlwaysUpdate=False):
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it
    if Unit in Devices:
        if Devices[Unit].nValue != nValue or Devices[Unit].sValue != sValue or Devices[Unit].TimedOut != TimedOut or AlwaysUpdate:
            Devices[Unit].Update(nValue=nValue, sValue=str(sValue), TimedOut=TimedOut)
            Domoticz.Debug("Update " + Devices[Unit].Name + ": " + str(nValue) + " - '" + str(sValue) + "'")
