#!/bin/bash

ifconfig wlan0 up
iwconfig wlan0 mode ad-hoc
iwconfig wlan0 essid "ESP"
iwconfig wlan0 channel 3
iwconfig wlan0 key s:password
iwconfig wlan0 inet 192.162.1.77
