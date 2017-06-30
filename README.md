# Dalek
Python code for Raspberry Pi 3 controlled Dalek

Files:

dalek.py - Dalek and Strobe classes
davros.py - simple CLI, instantiates a Dalek and allows text commands
wifi.py - instantiates a Dalek and listens for request on http socket and performs a simple control script

This code controls the following HATs:

Adafruit Servo - controls iris
Piface Relay - dome lights, gun, eye lights

audio is TTS using Espeak