DEVICE_TYPE = "RyanPi"
THING_NAME = "ryan-Pi"
# TOPICS list has tuples formatted as: (topic path, subscription function name to be pinned as callback function)
TOPICS = [("data", "controlFan"), ("GUItoggleFanControl", "GUItoggleFanControl"), ("GUIturnOnFan", "GUIturnOnFan"), ("GUIturnOffFan", "GUIturnOffFan")]
CLIENT_ID = "Sensor"
AWS_SERVER = "ayvv068gcr0us-ats.iot.us-west-1.amazonaws.com"
PORT = 8883

