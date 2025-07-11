#!/bin/bash

rm -f usb240.txt
rm -f lsb240.txt
rm -f dsb240.txt
rm -f ifspec.err

am example2.5.ifspec.amc 228 GHz  252 GHz  2 MHz  0 deg  277 K  0.5385  usb 240 GHz  \
>> usb240.txt 2>>ifspec.err

am example2.5.ifspec.amc 228 GHz  252 GHz  2 MHz  0 deg  277 K  0.5385  lsb 240 GHz  \
>> lsb240.txt 2>>ifspec.err

am example2.5.ifspec.amc 228 GHz  252 GHz  2 MHz  0 deg  277 K  0.5385  dsb 240 GHz \
>> dsb240.txt 2>>ifspec.err

