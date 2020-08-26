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
from functionalizedDynamoDB import insertRow, deleteTable, createTable


# Publication function for tripwire
entryNumber_tripwireTracking = 1
def tripwireTriggered(ev=None):
    global entryNumber_tripwireTracking
    test = "does not matter"
    payload = test
    print("Tripwire triggered.")
    myMQTTClient.publish("CameraModule/Camera1/picture", payload, 0)
    myMQTTClient.publish("RyanPi/ryan_pi/tripwire", payload, 0)
    # Track timestamp in DynamoDB
    now = datetime.utcnow()
    now_str_date = now.strftime('%Y-%m-%d')
    now_str_time = now.strftime('%H:%M:%S')

    DB = boto3.resource("dynamodb")
    tableName_tripwire = "tripwireTracking"
    primaryColumnName_tripwire = "entryNumber"
    columns_tripwire = ["date", "time"]
    tripwireTrackingTable = DB.Table(tableName_tripwire)
    insertRow(tripwireTrackingTable, columns_tripwire, primaryColumnName_tripwire, entryNumber_tripwireTracking, now_str_date, now_str_time)

    # Increment tripwire table's entry number
    entryNumber_tripwireTracking = entryNumber_tripwireTracking + 1


# Main execution start
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
    tableName_TempHum = "tempHumidityData"
    primaryColumnName_TempHum = "entryNumber"
    columns_TempHum = ["temperature", "humidity"]

    # Trigger timestamp table setup fields
    tableName_Tripwire = "tripwireTracking"
    primaryColumnName_Tripwire = "entryNumber"
    columns_Tripwire = ["date", "time"]

    # resource and client
    DB = boto3.resource("dynamodb")
    DB_client = boto3.client("dynamodb")

    # Create temperature and humidity table
    try:
        print("Attempting to create tempHumidityData table...")
        newTable_TempHum = createTable(DB, tableName_TempHum, primaryColumnName_TempHum)
        waiter = DB_client.get_waiter("table_exists")
        waiter.wait(TableName=tableName_TempHum)

    # Exception if table already exists, delete and recreate
    except DB_client.exceptions.ResourceInUseException as E:
        oldTable_TempHum = DB.Table(tableName_TempHum)
        deletedTable_TempHum = deleteTable(oldTable_TempHum)
        waiter = DB_client.get_waiter("table_not_exists")
        waiter.wait(TableName=tableName_TempHum)

        # Recreate the table now
        print("tempHumidityData table exists, deleting and creating fresh table...")
        newTable_TempHum = createTable(DB, tableName_TempHum, primaryColumnName_TempHum)
        waiter = DB_client.get_waiter("table_exists")
        waiter.wait(TableName=tableName_TempHum)

    except Exception as E:
        print(f"Unspecified exception occurred creating tempHumidityData table: " + str(E))
        exit()

    # Create tripwire tracking table
    try:
        print("Attempting to create tripwireTracking table...")
        newTable_Tripwire = createTable(DB, tableName_Tripwire, primaryColumnName_Tripwire)
        waiter = DB_client.get_waiter("table_exists")
        waiter.wait(TableName=tableName_Tripwire)

    # Exception if table already exists, delete and recreate
    except DB_client.exceptions.ResourceInUseException as E:
        oldTable_Tripwire = DB.Table(tableName_Tripwire)
        deletedTable_Tripwire = deleteTable(oldTable_Tripwire)
        waiter = DB_client.get_waiter("table_not_exists")
        waiter.wait(TableName=tableName_Tripwire)

        # Recreate the table now
        print("tripwireTracking table exists, deleting and creating fresh table...")
        newTable_Tripwire = createTable(DB, tableName_Tripwire, primaryColumnName_Tripwire)
        waiter = DB_client.get_waiter("table_exists")
        waiter.wait(TableName=tableName_Tripwire)

    except Exception as E:
        print(f"Unspecified exception occurred creating tripwireTracking table: " + str(E))
        exit()


    print("tempHumidityData and tripWireTracking tables successfully created!")

    entryNumber_TempHum = 1
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
                insertRow(newTable_TempHum, columns_TempHum, primaryColumnName_TempHum, entryNumber_TempHum, temperature, humidity)
                now = datetime.utcnow()
                now_str = now.strftime('%Y-%m-%d %H:%M:%S')
                payload = '{ "timestamp": "' + now_str + '","temperature": ' + str(temperature) + ',"humidity": '+ str(humidity) + ' }'
                myMQTTClient.publish("data", payload, 0)
            else:
                print("Failed to retrieve data from humidity sensor")

            # Increment temperature/humidity table's primary key value for next row entry
            entryNumber_TempHum = entryNumber_TempHum + 1
            # Sleep for 2 seconds, only read from temp/humidity sensor once every 2 seconds
            sleep(2)

        except KeyboardInterrupt:
            print("Keyboard interrupt, exiting program")
            GPIO.cleanup()
            exit()

        except Exception as E:
            print(f"Unspecified exception occurred in main application loop. Exception is: " + str(E))

