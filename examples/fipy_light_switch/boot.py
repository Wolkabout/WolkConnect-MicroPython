import os

import machine
from machine import UART

uart = UART(0, baudrate=115200)
os.dupterm(uart)

machine.main("main.py")
