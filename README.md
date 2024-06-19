# ISOXLIIS MicroPython Software

This is a very simple demo using MicroPython's USB HID features to drive
the ISOXLIIS keyboard.

Requires pico_usb-v1.23.0-1-pimoroni-micropython.uf2 
From: https://github.com/pimoroni/pimoroni-pico/releases/tag/v1.23.0-1

Features:

* Uses PIO to scan the matrix
* Uses MicroPython USB (easy to customise)
* Bailout keys, hold one of the following before plugging in USB or running isoxliis.py:
   * ESC - Do not boot firmware
   * Q - Do not enable USB
* Two layers