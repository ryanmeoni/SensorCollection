from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTThingJobsClient

import subprocess
import time
import subscriptionFunctions

from defines import * #TODO Find a better way to do this

CLIENT = "myClient"
AWS_SERVER = "ayvv068gcr0us-ats.iot.us-west-1.amazonaws.com"
PORT = 8883

CA_CERTIFICATE = "../Certificates/root-CA.crt"
PRIVATE_KEY = "../Certificates/device-private.pem.key"
DEVICE_CERTIFICATE = "../Certificates/device-certificate.pem.crt"

def AWS_MQTT_subscribe(MQTTClient, topic, function = None):
  print("Subscribing to topics")
  topicPath = DEVICE_TYPE +"/" + THING_NAME + "/"
  if topic == None:
    for t in TOPICS:
      callbackFunction = subscriptionFunctions.generateCallbackFunction(t)
      print(topicPath + t)
      if MQTTClient.subscribe(topicPath + t, 1, callbackFunction):
        print(t + " Subscription successful")
        #return True

  else:
    #TODO
    print("Custom topic subscription for testing")
    topicPath = DEVICE_TYPE +"/" + THING_NAME + "/" + topic
    if MQTTClient.subscribe(topicPath, 1, function):
      return True
  return False

def AWS_MQTT_Initialize():
  global CA_CERTIFICATE
  global PRIVATE_KEY
  global DEVICE_CERTIFICATE
  try:
    subprocess.call('./copyCertificates.sh')
  except:
    CA_CERTIFICATE = "Certificates/root-CA.crt"
    PRIVATE_KEY = "Certificates/device-private.pem.key"
    DEVICE_CERTIFICATE = "Certificates/device-certificate.pem.crt"
  #AWS IoT certificate based connection---------------------------------------
  myMQTTClient = AWSIoTMQTTClient(CLIENT)#this can be any arbitrary string
  myMQTTClient.configureEndpoint(AWS_SERVER, PORT)#endpoint and port number
  myMQTTClient.configureCredentials(CA_CERTIFICATE, PRIVATE_KEY, DEVICE_CERTIFICATE)#root ca and certificate used for secure connection

  myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
  myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
  myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
  myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

  #connect, subscribe and publish----------------------------------------------------------
  myMQTTClient.connect()
  AWS_MQTT_subscribe(myMQTTClient, None)
  myMQTTClient.publish(THING_NAME + "/info", "connected", 0)
  return myMQTTClient

