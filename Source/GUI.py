import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import sys
from matplotlib import style
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tkinter import ttk
import tkinter as tk
import matplotlib
from decimal import Decimal
matplotlib.use("TkAgg")


class StartPage(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        button1 = ttk.Button(self, text="Reset", command=reset_graphs)
        button1.pack()
        button2 = ttk.Button(self, text="Take Picture",
                             command=takePicture)
        button2.pack()
        button3 = ttk.Button(self, text="Toggle Fan Control",
                             command=toggleFanControl)
        button3.pack()
        button4 = ttk.Button(self, text="Turn Fan On", command=turnOnFan)
        button4.pack()
        button5 = ttk.Button(self, text="Turn Fan Off", command=turnOffFan)
        button5.pack()
        button6 = ttk.Button(self, text="Toggle Motor Control",
                             command=toggleMotorControl)
        button6.pack()
        button7 = ttk.Button(self, text="Turn Motor On", command=turnMotorOn)
        button7.pack()
        button8 = ttk.Button(self, text="Turn Motor Off", command=turnMotorOff)
        button8.pack()
        button9 = ttk.Button(self, text="Exit Program", command=quitProgram)
        button9.pack()

        canvas = FigureCanvasTkAgg(fig, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


class graphApp(tk.Tk):

    def __init__(self, *args, **kwargs):

        root = tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "Extensible Sensor Network")
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=5)
        container.grid_columnconfigure(0, weight=5)
        self.frames = {}
        frame = StartPage(container, self)
        self.frames[StartPage] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(StartPage)

    # Function to display frame in window (allows creation of more frames, but I don't think I need more than 1)
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


# Data fields needed for plotting live data
entryCountTempHum = 0
entryCountLightLevel = 0
pause_start = 0
temperatureGraph_x = []
temperatureGraph_y = []
humidityGraph_x = []
humidityGraph_y = []
lightLevel_x = []
lightLevel_y = []
time = 0
maxLightLevel = 0
currLightLevel = 0
currTemperature = 0
currHumidity = 0
avgTemperature = 0
avgHumidity = 0
avgTemperature = 0

#tripwireActivationCount = 0

# Set up our plots
fig = plt.figure(figsize=(6, 4))
#fig.suptitle(f"Tripwire Activations: {tripwireActivationCount}", fontsize=12)
sub1 = plt.subplot(2, 3, 1)
sub2 = plt.subplot(2, 3, 2)
sub3 = plt.subplot(2, 3, 3)
#sub4 = plt.subplot(2, 2, 4)
sub1.set_title(
    "Average Temperature: Waiting...\nCurrent Temperature: Waiting...\n \nTemperature vs. Entries", fontsize=10)
sub1.set_ylabel("Temperature (C)")
sub1.set_xlabel("Temperature Entries")
sub2.set_title(
    "Average Humidity: Waiting...\nCurrent Humidity: Waiting...\n \nHumidity vs. Entries", fontsize=10)
sub2.set_ylabel("Humidity (%)")
sub2.set_xlabel("Humidity Entries")
sub3.set_title(
    "Max Light Level: Waiting...\nCurrent Light Level: Waiting...\n \nLight Level vs. Entries", fontsize=10)
sub3.set_ylabel("Light Level (%)")
sub3.set_xlabel("Light Level Entries")

# Plot once to set labels
sub1.plot(temperatureGraph_x, temperatureGraph_y,
          color='blue', label='Temperature')
sub1.legend(loc='upper right')
sub1.set_xlim(left=max(0, entryCountTempHum - 50),
              right=entryCountTempHum + 25)
sub2.plot(humidityGraph_x, humidityGraph_y, color='red', label='Humidity')
sub2.legend(loc='upper right')
sub2.set_xlim(left=max(0, entryCountTempHum - 50),
              right=entryCountTempHum + 25)
sub3.plot(lightLevel_x, lightLevel_y, color='green', label='Light Level')
sub3.legend(loc='upper right')
sub3.set_xlim(left=max(0, entryCountLightLevel - 50),
              right=entryCountLightLevel + 25)


# Animation function to update plot


def animate(i):
    global entryCountTempHum
    global pause_start
    global time
    global temperatureGraph_x
    global temperatureGraph_y
    global humidityGraph_x
    global humidityGraph_y
    global lightLevel_x
    global lightLevel_y
    global avgHumidity
    global avgTemperature
    global currHumidity
    global currTemperature
    global maxLightLevel
    global currLightLevel
    global sub1
    global sub2
    global sub3

    try:
        sub1.plot(temperatureGraph_x, temperatureGraph_y, color='blue')
        sub1.set_xlim(left=max(0, entryCountTempHum - 50),
                      right=entryCountTempHum + 25)
        sub2.plot(humidityGraph_x, humidityGraph_y, color='red')
        sub2.set_xlim(left=max(0, entryCountTempHum - 50),
                      right=entryCountTempHum + 25)
        sub3.plot(lightLevel_x, lightLevel_y, color='green')
        sub3.set_xlim(left=max(0, entryCountLightLevel - 50),
                      right=entryCountLightLevel + 25)
        sub1.set_title(
            f"Average Temperature: {avgTemperature} C\nCurrent Temperature: {currTemperature} C\n \nTemperature vs. Entries", fontsize=10)
        sub2.set_title(
            f"Average Humidity: {avgHumidity}%\nCurrent Humidity: {currHumidity}%\n \nHumidity vs. Entries", fontsize=10)
        sub3.set_title(
            f"Max Light Level: {maxLightLevel}%\nCurrent Light Level: {currLightLevel}%\n \nLight Level vs. Entries", fontsize=10)

    except:
        print(f"Error occurred in plotting data at tempHumEntryCount = {entryCountTempHum}")

    # Increment time
    time += 1
    # Update averages every 5 seconds
    updateAverages(time)


# Reset Graph Data
def reset_graphs():
    global sub1
    global sub2
    global sub3
    global entryCountTempHum
    global entryCountLightLevel
    global temperatureGraph_x
    global temperatureGraph_y
    global humidityGraph_x
    global humidityGraph_y
    global lightLevel_x
    global lightLevel_y
    #global tripwireActivationCount
    global fig
    global maxLightLevel
    global currLightLevel
    global currTemperature
    global currHumidity
    global avgHumidity
    global avgTemperature

    sub1.clear()
    sub2.clear()
    sub3.clear()
    sub1.set_title(
        "Average Temperature: Waiting...\nCurrent Temperature: Waiting...\n \nTemperature vs. Entries", fontsize=10)
    sub1.set_ylabel("Temperature (Celcius)")
    sub1.set_xlabel("Temperature Entries")
    sub2.set_title(
        "Average Humidity: Waiting...\nCurrent Temperature: Waiting...\n \nHumidity vs. Entries", fontsize=10)
    sub2.set_ylabel("Humidity (%)")
    sub2.set_xlabel("Humidity Entries")
    sub3.set_title(
        "Max Light Level: Waiting...\nCurrent Light Level: Waiting...\n \nLight Level vs. Entries", fontsize=10)
    sub3.set_ylabel("Light Level (%)")
    sub3.set_xlabel("Light Level Entries")
    
    entryCountTempHum = 0
    entryCountLightLevel = 0
    maxLightLevel = 0
    currLightLevel = 0
    currTemperature = 0
    currHumidity = 0
    avgTemperature = 0
    avgHumidity = 0
    temperatureGraph_x.clear()
    temperatureGraph_y.clear()
    humidityGraph_x.clear()
    humidityGraph_y.clear()
    lightLevel_x.clear()
    lightLevel_y.clear()
    
    sub1.plot(temperatureGraph_x, temperatureGraph_y,
          color='blue', label='Temperature')
    sub1.legend(loc='upper right')
    sub1.set_xlim(left=max(0, entryCountTempHum - 50),
              right=entryCountTempHum + 25)
    sub2.plot(humidityGraph_x, humidityGraph_y, color='red', label='Humidity')
    sub2.legend(loc='upper right')
    sub2.set_xlim(left=max(0, entryCountTempHum - 50),
              right=entryCountTempHum + 25)
    sub3.plot(lightLevel_x, lightLevel_y, color='green', label='Light Level')
    sub3.legend(loc='upper right')
    sub3.set_xlim(left=max(0, entryCountLightLevel - 50),
              right=entryCountLightLevel + 25)

    #tripwireActivationCount = 0
    #fig.suptitle(f"Tripwire Activations: {tripwireActivationCount}", fontsize=12)

# Function to start or pause graphs


def takePicture():
    payload = "doesn't matter"
    myMQTTClient.publish("CameraModule/Camera1/picture", payload, 0)


def humidityTempUpdate(self, params, packet):
    global entryCountTempHum
    global temperatureGraph_x
    global temperatureGraph_y
    global humidityGraph_x
    global humidityGraph_y
    global currHumidity
    global currTemperature

    payloadDict = json.loads(packet.payload)

    Temp = Decimal(payloadDict["temperature"])
    Temp = round(Temp, 2)
    Humidity = Decimal(payloadDict["humidity"])
    Humidity = round(Humidity, 2)

    # Increment total number of entries stored in program
    entryCountTempHum += 1

    # Push values to arrays for plotting
    temperatureGraph_y.append(Temp)
    temperatureGraph_x.append(entryCountTempHum)
    humidityGraph_y.append(Humidity)
    humidityGraph_x.append(entryCountTempHum)
    currTemperature = Temp
    currHumidity = Humidity


def lightLevelUpdate(self, params, packet):
    global sub3
    global entryCountLightLevel
    global lightLevel_x
    global lightLevel_y
    global maxLightLevel
    global currLightLevel

    payloadDict = json.loads(packet.payload)
    lightLevel = Decimal(payloadDict["Light"])
    lightLevel = round(lightLevel, 2)

    # Increment total number of entries stored in program
    entryCountLightLevel += 1

    # Push values to arrays for plotting
    lightLevel_y.append(lightLevel)
    lightLevel_x.append(entryCountLightLevel)

    # Update max and curr light level
    maxLightLevel = max(lightLevel, maxLightLevel)
    currLightLevel = lightLevel
    


def updateAverages(time):
    global avgHumidity
    global avgTemperature
    if (time % 5 == 0):

        try:

            tableName = "tempHumidityData"
            primaryColumnName = "entryNumber"

            # resource
            DB = boto3.resource("dynamodb")
            table = DB.Table(tableName)

            response = table.scan(
                FilterExpression=Attr(primaryColumnName).gte(0)
            )

            totalValues = 0
            humiditySum = 0
            temperatureSum = 0

            for row in response["Items"]:
                humiditySum += row["humidity"]
                temperatureSum += row["temperature"]
                totalValues += 1

            humidityAvg = humiditySum / totalValues
            temperatureAvg = temperatureSum / totalValues
            humidityAvg = round(humidityAvg, 2)
            temperatureAvg = round(temperatureAvg, 2)

            # Update averages
            avgHumidity = humidityAvg
            avgTemperature = temperatureAvg

        except:
            print("An exception occurred in update averages")


# def updateActivationCount(client, userdate, message):
    #global tripwireActivationCount
    #tripwireActivationCount += 1
    #fig.suptitle(f"Tripwire Activations: {tripwireActivationCount}", fontsize=12)


def toggleFanControl():
    myMQTTClient.publish("RyanPi/ryan-Pi/GUItoggleFanControl",
                         "payload doesn't matter", 0)


def toggleMotorControl():
    myMQTTClient.publish(
        "MotorController/reynaPi/GUItoggleMotorControl", "payload doesn't matter", 0)


def turnOnFan():
    myMQTTClient.publish("RyanPi/ryan-Pi/GUIturnOnFan",
                         "payload doesn't matter", 0)


def turnOffFan():
    myMQTTClient.publish("RyanPi/ryan-Pi/GUIturnOffFan",
                         "payload doesn't matter", 0)


def turnMotorOn():
    myMQTTClient.publish(
        "MotorController/reynaPi/GUIturnOnMotor", "payload doesn't matter", 0)


def turnMotorOff():
    myMQTTClient.publish(
        "MotorController/reynaPi/GUIturnOffMotor", "payload doesn't matter", 0)


def quitProgram():
    exit()


if __name__ == "__main__":
    try:

        # MQTT setup
        myMQTTClient = AWSIoTMQTTClient("theGUI-ID")
        myMQTTClient.configureEndpoint(
            "a3te7fgu4kv468-ats.iot.us-west-1.amazonaws.com", 8883)
        myMQTTClient.configureCredentials("/home/ryan/Certificates/RootCA.crt",
                                          "/home/ryan/Certificates/78ac4c9e75-private.pem.key", "/home/ryan/Certificates/78ac4c9e75-certificate.pem.crt")
        myMQTTClient.configureOfflinePublishQueueing(-1)
        myMQTTClient.configureDrainingFrequency(2)
        myMQTTClient.configureConnectDisconnectTimeout(10)
        myMQTTClient.configureMQTTOperationTimeout(5)
        myMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
        myMQTTClient.connect()
        myMQTTClient.subscribe("RyanPi/ryan_pi/data", 1, humidityTempUpdate)
        #myMQTTClient.subscribe("RyanPi/ryan_pi/tripwire", 1, updateActivationCount)
        myMQTTClient.subscribe("Pi_sense01/data", 1, lightLevelUpdate)

        app = graphApp()
        app.minsize(1250, 900)
        ani = animation.FuncAnimation(fig, animate, interval=1000)
        app.mainloop()

    except (KeyboardInterrupt):
        print("Exiting")
