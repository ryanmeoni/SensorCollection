import RPi.GPIO as GPIO
import json
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import os
import sys
import boto3
import Adafruit_DHT
from time import sleep
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal
from datetime import date, datetime
import functionalizedAWSIOT
import subscriptionFunctions

def insertRow(table, columns, primaryColumnName, entryNumber, attributeOne, attributeTwo):
    # test that we can insert a new row into table with a given primary key (entryNumber)

    response = table.put_item(
        Item={
            primaryColumnName: entryNumber,
            columns[0]: attributeOne,
            columns[1]: attributeTwo
        }
    )


def printAllRows(table, primaryColumnName):
    # print all table entries to test we inserted rows correctly
    # get all rows with a primary key (entryNumber) greater than or equal to 0 (so all of them)

    response = table.scan(
        FilterExpression=Attr(primaryColumnName).gte(0)
    )

    for row in response["Items"]:
        print(row)

def createTable(DB, tableName, primaryColumnName):

    table = DB.create_table(
        TableName=tableName,
        KeySchema=[
            {
                'AttributeName': primaryColumnName,
                'KeyType': 'HASH'  # Partition key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': primaryColumnName,
                'AttributeType': 'N'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    return table

def deleteTable(table):
    table.delete()
    return table

# Publication function for tripwire
entryNumber_trigger = 0
def tripwireTriggered(ev=None):
    global entryNumber_trigger
    test = "does not matter"
    payload = test
    print("Tripwire triggered.")
    myMQTTClient.publish("CameraModule/Camera1/picture", payload, 0)
    myMQTTClient.publish("RyanPi/ryan_pi/tripwire", payload, 0)
    # Track timestamp in DynamoDB
    now = datetime.utcnow()
    now_str_date = now.strftime('%Y-%m-%d')
    now_str_time = now.strftime('%H:%M:%S')

    #    DB = boto3.resource("dynamodb")
    tableName_trigger = "tripwireTracking"
    primaryColumnName_trigger = "entryNumber"
    columns_trigger = ["date", "time"]
    #    triggerTable = DB.Table(tableName_trigger)
    #    insertRow(triggerTable, columns_trigger, primaryColumnName_trigger, entryNumber_trigger, now_str_date, now_str_time)

    # Increment tripwire table's entry number
    entryNumber_trigger = entryNumber_trigger + 1

# Main function
if __name__ == "__main__":

    # Initialize MQTT client
    myMQTTClient = functionalizedAWSIOT.AWS_MQTT_Initialize()

    # GPIO set up
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Specify the component/pin to be used for temp/humidity sensor
    DHT_SENSOR = Adafruit_DHT.DHT22
    DHT_PIN = 20
    # Pins for fan
    GPIO.setup(16, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.output(16, GPIO.HIGH)
    # Pins for tripwire
    GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(21, GPIO.FALLING, callback=tripwireTriggered, bouncetime=5000)

    # entryNumber is primary key for both tables

    # Temperature/Humidity data table setup fields
    tableName_tempHum = "tempHumidityData"
    primaryColumnName_tempHum = "entryNumber"
    columns_tempHum = ["temperature", "humidity"]

    # Trigger timestamp table setup fields
    tableName_trigger = "tripwireTracking"
    primaryColumnName_trigger = "entryNumber"
    columns_trigger = ["date", "time"]

    # resource
    #      DB = boto3.resource("dynamodb")
    #      oldTable_tempHum = DB.Table(tableName_tempHum)
    #      oldTable_trigger = DB.Table(tableName_trigger)

    # Delete existing table
    #      oldTableTempHum = deleteTable(oldTable_tempHum)
    #      oldTableTrigger = deleteTable(oldTable_trigger)

    # 3 second sleep to give tables time to be deleted on AWS
    sleep(5)
    print("OLD TABLES DELETED")

    # Create new tables
    #      newTableTempHum = createTable(DB, tableName_tempHum, primaryColumnName_tempHum)
    #      newTableTrigger = createTable(DB, tableName_trigger, primaryColumnName_trigger)

    #5 second sleep to give tables time to be created on AWS
    sleep(7)
    print("NEW TABLES CREATED")

    # test insert row with entryNumber of 1
    entryNumber_tempHum = 1

    while True:
        try:
            temperature = None
            humidity = None
            humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
            if humidity is not None and temperature is not None:

                temperature = Decimal(temperature)
                temperature = round(temperature, 2)
                humidity = Decimal(humidity)
                humidity = round(humidity, 2)
                print(f"Temperature: {temperature}, Humidity: {humidity}")
                print("####")
                #    insertRow(newTableTempHum, columns_tempHum, primaryColumnName_tempHum, entryNumber_tempHum, temperature, humidity)
                now = datetime.utcnow()
                now_str = now.strftime('%Y-%m-%d %H:%M:%S')
                payload = '{ "timestamp": "' + now_str + '","temperature": ' + str(temperature) + ',"humidity": '+ str(humidity) + ' }'
                myMQTTClient.publish("RyanPi/ryan-Pi/controlFan", payload, 0)
            else:
                print("Failed to retrieve data from humidity sensor")

            # Increment temperature/humidity table's primary key value for next row entry
            entryNumber_tempHum = entryNumber_tempHum + 1
            # Sleep for 2 seconds, only grab values every 2 seconds
            sleep(2)

        except KeyboardInterrupt:
            print("Keyboard interrupt, exiting program")
            GPIO.cleanup()
            exit()

        except:
            print("Error publishing")
            #GPIO.cleanup()
            #exit()

