from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTThingJobsClient
import subprocess
import time
import subscriptionFunctions
import defines
import sys

# Function that subscribes to topics in defines.py on MQTT client creation
def AWS_MQTT_auto_subscribe(MQTTClient):
  print("Subscribing to topics")
  for topic in defines.TOPICS:
    topicPath = topic[0]
    callbackFunctionName = topic[1]
    print(f"Looking for function {callbackFunctionName}")
    callbackFunction = subscriptionFunctions.generateCallbackFunction(callbackFunctionName)
    print(f"Current topic being subscribed to is: {topicPath}")
    if MQTTClient.subscribe(topicPath, 1, callbackFunction):
      print(f"{topicPath} Subscription successful")


# Function to explicity subscribe to topics
def AWS_MQTT_subscribe(MQTTClient, topic, callbackFunction):
  MQTTClient.subscribe(topic, 1, callbackFunction)


# Function to explicity publish to topics
def AWS_MQTT_publish(MQTTClient, topic, payload):
  MQTTClient.publish(topic, payload, 0)


def AWS_MQTT_Initialize():
  # Setup certificates
  CA_CERTIFICATE = None
  PRIVATE_KEY = None
  DEVICE_CERTIFICATE = None
  try:
    subprocess.call('./copyCertificates.sh')
    CA_CERTIFICATE = "../Certificates/root-CA.crt"
    PRIVATE_KEY = "../Certificates/device-private.pem.key"
    DEVICE_CERTIFICATE = "../Certificates/device-certificate.pem.crt"
  except:
    print("Exception in running copyCertificates.sh")
    exit(-1)

  # AWS IoT certificate based connection---------------------------------------
  myMQTTClient = AWSIoTMQTTClient(defines.CLIENT_ID)#this can be any arbitrary string
  myMQTTClient.configureEndpoint(defines.AWS_SERVER, defines.PORT) #endpoint and port number
  myMQTTClient.configureCredentials(CA_CERTIFICATE, PRIVATE_KEY, DEVICE_CERTIFICATE) #root ca and certificate used for secure connection

  myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
  myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
  myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
  myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

  # connect, subscribe and publish----------------------------------------------------------
  myMQTTClient.connect()
  AWS_MQTT_auto_subscribe(myMQTTClient)
  return myMQTTClient

