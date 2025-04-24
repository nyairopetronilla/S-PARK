import serial
import time

# Replace 'COM7' with your correct Arduino port if needed
arduino = serial.Serial('COM11', 9600)
time.sleep(2)  # Give it time to start

while True:
    if arduino.in_waiting:
        data = arduino.readline().decode('utf-8').strip()
        print(data)
