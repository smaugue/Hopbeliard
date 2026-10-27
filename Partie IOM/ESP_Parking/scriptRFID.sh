#!/bin/bash

infoCarte=$(nfc-list | grep "UID" | awk -F': ' '{print $2}')

mosquitto_pub -h 10.2.2.248 -p 1883 -t "test/RFID" -m "$infoCarte";