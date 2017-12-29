# Domoticz-Motion-in-room

## Description
Motion sensors indicate whether they see motion. However if you want to control lights in your room depending on motion detected, you want to be sure only to switch off the lights if motion is not detected for x minutes.
With this plugin it is possible to control this.

## Installation
Python version 3.4 or higher required & Domoticz version 3.87xx or greater.
To install:
* Go in your Domoticz directory using a command line and open the plugins directory.
* Run: ```git clone https://github.com/Xorfor/Domoticz-Pi-hole-Plugin.git```
* Restart Domoticz with ```sudo systemctl restart domoticz```.

In the web UI, navigate to the Hardware page. In the hardware dropdown there will be an entry called "Pi-hole summary".

## Updating
To update:
* Go in your Domoticz directory using a command line and open the plugins directory then the Domoticz-Pi-hole-Plugin directory.
* Run: ```git pull```
* Restart Domoticz with ```sudo systemctl restart domoticz```.

## Parameters
| Parameter | Value |
| :--- | :--- |
| **Domoticz server** |  Address of the Domiticz server with motion detector, eg. localhost, or 192.168.1.231. Default is localhost. |
| **Port** | Port of the Domiticz server with motion detector. Default is 8080. |
| **IDX** | List of idx values of the motion sensors on the Domticz server. |
| **Debug** | Default is False |
