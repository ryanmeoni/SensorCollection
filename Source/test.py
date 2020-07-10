import sys
import fake_rpi
sys.modules['RPi'] = fake_rpi.RPi     # Fake RPi
sys.modules['RPi.GPIO'] = fake_rpi.RPi.GPIO # Fake GPIO

import subscriptionFunctions
import pytest #My local machine doesn't like this
import inspect
import json
import time
from functionalizedDynamoDB import createTable, deleteTable, insertRow
import boto3
import string
import random

#Mock class for packet
class message:
  payload = None
  topic = None

  def __init__(self, payload):
    self.payload = payload

functionList = list(subscriptionFunctions.subscribedTopicDictionary.values()) #Get the list of all callback functions

@pytest.mark.parametrize("function", functionList) #Tests that the callback functions have the proper signature
def test_publishFunctionSignatures(function):
  assert len(inspect.signature(function).parameters) == 3

#Tests for DC fan below 

#Test data
data1 = '{ "temperature": ' + "20" + ',"humidity": '+ "50" + ' }'
data2 = '{ "temperature": ' + "40" + ',"humidity": '+ "100" + ' }'
data3 = '{ "temperature": ' + "15" + ',"humidity": '+ "86" + ' }'
data4 = '{ "temperature": ' + "99" + ',"humidity": '+ "84" + ' }'
message1 = message(data1)
message2 = message(data2)
message3 = message(data3)
message4 = message(data4)

@pytest.mark.parametrize("message, expectedStatus", [(message1, 0), (message2, 1), (message3, 1), (message4, 0)])
def test_fanOperational(message, expectedStatus):
  assert subscriptionFunctions.controlFan("Testing", "Testing", message) == expectedStatus

# Tests for GUI triggered callback functions

def test_GUIturnOnFan_enabled():
  assert subscriptionFunctions.GUIturnOnFan("Test enabled", "Test enabled", None) == 1

def test_GUIturnOnFan_disabled():
  assert subscriptionFunctions.GUIturnOnFan("Test disabled", "Test disabled", None) == 0

def test_GUIturnOffFan_enabled():
  assert subscriptionFunctions.GUIturnOffFan("Test enabled", "Test enabled", None) == 1

def test_GUIturnOffFanControl_disabled():
  assert subscriptionFunctions.GUIturnOffFan("Test disabled", "Test disabled", None) == 0

def test_GUItoggleFanControl_toggleOn():
  assert subscriptionFunctions.GUItoggleFanControl("Toggle on", "Toggle on", None) == 1

def test_GUItoggleFanControl_toggleOff():
  assert subscriptionFunctions.GUItoggleFanControl("Toggle off", "Toggle off", None) == 0


# Test insertRow() function for DynamoDB using insertRow() function from temperatureHumidity.py
def test_insertDynamoRow():
  DB = boto3.resource("dynamodb")
  insertionTable = DB.Table("testInsertTable")
  columns = ["Robot Noise 1", "Robot Noise 2"]
  primaryColumnName = "Random String Key"
  attributeOne = "Boop"
  attributeTwo = "Beep"

  # Method to generate random string used from here: https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits
  entryString = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(15))

  # Check the number of rows in table before insertion
  response = insertionTable.scan()
  tableSizeBefore = len(response["Items"])

  # Insert new row
  insertRow(insertionTable, columns, primaryColumnName, entryString, attributeOne, attributeTwo)
  time.sleep(1)

  # Check the number of rows in table after insertion
  response = insertionTable.scan()
  tableSizeAfter = len(response["Items"])

  assert tableSizeAfter - tableSizeBefore == 1
