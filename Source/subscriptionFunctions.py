import cameraCode
import reynaPiNode
import helpers
import RPi.GPIO as GPIO
import functionalizedRadio
import json
from decimal import Decimal

#radio = functionalizedRadio.initializeRadio()#will this conflict with other Things/Pi's? (potential for GPIO issue but this resolves pytest issue)

GUI_control_fan = 0
GUI_control_motor = 0

# Should be in form customCallback(client, userdata, message)
# where message contains topic and payload.
# Note that client and userdata are here just to be aligned with the underneath Paho callback function signature.
# These fields are pending to be deprecated and should not be depended on.

def picture(client, userdata, message):
    bucketName = "senior-design-camera-files"
    try:
        fileName = cameraCode.takePicture()
        helpers.uploadToS3(fileName[0], bucketName,
                           helpers.getAWSCredentials())
    finally:
        print("Taking picture and uploading to S3 bin")
        return True


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


def data(self, params, packet):
  print("")


# Function to toggle GUI's motor control (triggered from button)
def GUItoggleMotorControl(client, userdata, message):
  global GUI_control_motor

  if (client == "Toggle on" and userdata == "Toggle on"):
    GUI_control_motor = 0

  if (client == "Toggle off" and userdata == "Toggle off"):
    GUI_control_motor = 1

  if (GUI_control_motor == 0):
    GUI_control_motor = 1
    print(f"Toggled GUI motor control, GUI_control_motor is now {GUI_control_motor}")
    # Turn off motor on toggle of motor control, give control of motor to GUI
    reynaPiNode.stop2()
    return 1

  elif (GUI_control_motor == 1):
    GUI_control_motor = 0
    print(f"Toggled GUI motor control, GUI_control_motor is now {GUI_control_motor}")
    # Turn off motor on toggle of motor control, give control of motor back to sensor
    reynaPiNode.stop2()
    return 0


def GUIturnOnMotor(client, userdata, message):
  global GUI_control_motor

  if (client == "Test enabled" and userdata == "Test enabled"):
    GUI_control_motor = 1

  if (client == "Test disabled" and userdata == "Test disabled"):
    GUI_control_motor = 0

  if (GUI_control_motor == 1):
    print("GUI turning on motor2")
    # Turn motor on
    reynaPiNode.go2()
    return 1

  return 0


def GUIturnOffMotor(client, userdata, message):
  global GUI_control_motor

  if (client == "Test enabled" and userdata == "Test enabled"):
    GUI_control_motor = 1

  if (client == "Test disabled" and userdata == "Test disabled"):
    GUI_control_motor = 0

  if (GUI_control_motor == 1):
    print("GUI turning off motor2")
    # Turn motor off
    reynaPiNode.stop2()
    return 1

  return 0


def ultrasonic(client, userdata, message):
  distance=0
  payloadInfo = json.loads(message.payload)
  distance = payloadInfo["distance"]
  if distance<15:
    reynaPiNode.stop1()
    return 0
  else:
    reynaPiNode.go1()
    return 1


def motor2(client, userdata, message):

  if (client == "Testing" and userdata == "Testing"):
    GUI_control_motor = 0

  humidity=0
  payloadInfo = json.loads(message.payload)
  humidity = payloadInfo["humidity"]
  print("humidity:", str(humidity))
  humidity = int(humidity)
  if humidity < 65 and GUI_control_motor == 0:
    reynaPiNode.stop2()
    return 0
  elif humidity >= 65 and GUI_control_motor == 0:
    reynaPiNode.go2()
    return 1


# subscribe to Ryan's humidity/temperature sensor-----
def subHumiture(client, userdate, message):
    payloadInfo = json.loads(message.payload)   
    humidity = payloadInfo["humidity"]
    temperature = payloadInfo["temperature"]
    #global radio #does nada ?
    Humidity_Threshold = 80.0

    print("\nRyan's Humiture Data:")
    print("Temperature: ", str(temperature), "\tHumidity:", str(humidity))

    if float(humidity) > Humidity_Threshold:  # print warning if threshold reached
        print("HIGH HUMIDITY THRESHOLD REACHED!\n")
        try:
             radio.send(21, "1", attempts=1)
             print ("LED Control Message -> On")  
        except:
            print ("Radio Error Occured")
        return 1

    if float(humidity) <= Humidity_Threshold:
        try:
            radio.send(21, "0", attempts=1)
            #print ("LED Control Message -> Off")
            print("")
        except:
            print ("Radio Error Occured")
                
        return 0        


# subscribe to Sky's radio network data------------------
def subRadioNodes(client, userdate, message):
    payloadInfo = json.loads(message.payload)
    myTemp = float(payloadInfo["Temperature"])
    myLight = int(payloadInfo["Light"])
    print("\nRadio Network Data: ")

    #print values from active nodes only
    if (myTemp != -999):  # print only if not default value
        print("Temperature: " + str(myTemp) + " C")

    if (myLight != -1):
        print("Light level: " + str(myLight) + "%")

    print("\n")

    
# subscribe to Reyna's ultrasonic sensor data-------------
def subUltrasonic(client, userdate, message):
    payloadInfo = json.loads(message.payload)
    distance = payloadInfo["distance"]
    print("Reyna's Sensor Data: ")
    print("Distance: ", int(distance))
    print("\n")

 
subscribedTopicDictionary = {
    "picture": picture,
    "controlFan": controlFan,
    "ultrasonic": ultrasonic,
    "motor2": motor2,
    "subHumiture": subHumiture,
    "subRadioNodes": subRadioNodes,
    "subUltrasonic": subUltrasonic,
    "GUItoggleFanControl" : GUItoggleFanControl,
    "GUIturnOnFan" : GUIturnOnFan,
    "GUIturnOffFan" : GUIturnOffFan,
    "data" : data,
    "GUIturnOnMotor" : GUIturnOnMotor,
    "GUIturnOffMotor" : GUIturnOffMotor,
    "GUItoggleMotorControl" : GUItoggleMotorControl
    # FIXME Find some way to not hardcode value names
}


# https://stackoverflow.com/questions/9168340/using-a-dictionary-to-select-function-to-execute
# Maybe check if k is valid input
def generateCallbackFunction(k):
    return subscribedTopicDictionary[k]

  
#####################################################################
# Custom callback functions for testing purposes only
#####################################################################
GLOBAL_TEST_VARIABLE = 0
def testCallbackFunction(client, userdata, message):
  global GLOBAL_TEST_VARIABLE
  GLOBAL_TEST_VARIABLE += 1

