#!/bin/bash

ifconfig wlan0 up
iwconfig wlan0 mode ad-hoc
iwconfig wlan0 essid ""
iwconfig wlan0 inet 192.162.1.42