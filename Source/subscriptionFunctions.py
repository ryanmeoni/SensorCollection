import RPi.GPIO as GPIO
import json
from decimal import Decimal

GUI_control_fan = 0
GUI_control_motor = 0

# Function to toggle GUI's fan control (triggered from button)
def GUItoggleFanControl(client, userdata, message):
  global GUI_control_fan

  if (client == "Toggle on" and userdata == "Toggle on"):
    GUI_control_fan = 0

  if (client == "Toggle off" and userdata == "Toggle off"):
    GUI_control_fan = 1

  if (GUI_control_fan == 0):
    GUI_control_fan = 1
    print(f"Toggled GUI fan control, GUI_control_fan is now {GUI_control_fan}")
    # Turn off fan on toggle of fan control, give control of fan to GUI
    GPIO.output(16, GPIO.HIGH)
    return 1

  elif (GUI_control_fan == 1):
    GUI_control_fan = 0
    print(f"Toggled GUI fan control, GUI_control_fan is now {GUI_control_fan}")
    # Turn off fan on toggle of fan control, give control of fan back to sensor
    GPIO.output(16, GPIO.HIGH)
    return 0


def GUIturnOnFan(client, userdata, message):
  global GUI_control_fan

  if (client == "Test enabled" and userdata == "Test enabled"):
    GUI_control_fan = 1

  if (client == "Test disabled" and userdata == "Test disabled"):
    GUI_control_fan = 0

  if (GUI_control_fan == 1):
    # Turn fan on
    print("GUI turning on fan")
    GPIO.output(16, GPIO.LOW)
    return 1

  return 0


def GUIturnOffFan(client, userdata, message):
  global GUI_control_fan

  if (client == "Test enabled" and userdata == "Test enabled"):
    GUI_control_fan = 1

  if (client == "Test disabled" and userdata == "Test disabled"):
    GUI_control_fan = 0

  if (GUI_control_fan == 1):
    # Turn fan off
    print("GUI turning off fan")
    GPIO.output(16, GPIO.HIGH)
    return 1

  return 0


def controlFan(client, userdata, message):
  global GUI_control_fan

  if (client == "Testing" and userdata == "Testing"):
    GUI_control_fan = 0

  print("SUP MAN")

  payloadDict = json.loads(message.payload)
  humidity = Decimal(payloadDict["humidity"])

  # Note GUI_control_fan in conditionals
  if (humidity > 85 and GUI_control_fan == 0):
    # Turning fan on
    GPIO.output(16, GPIO.LOW)
    return 1

  elif (humidity <= 85 and GUI_control_fan == 0):
    # Turning fan off
    GPIO.output(16, GPIO.HIGH)
    return 0

 
subscribedTopicDictionary = {
    "controlFan": controlFan,
    "GUItoggleFanControl" : GUItoggleFanControl,
    "GUIturnOnFan" : GUIturnOnFan,
    "GUIturnOffFan" : GUIturnOffFan
}

# https://stackoverflow.com/questions/9168340/using-a-dictionary-to-select-function-to-execute
# Maybe check if k is valid input
def generateCallbackFunction(topic):
    return subscribedTopicDictionary[topic]

