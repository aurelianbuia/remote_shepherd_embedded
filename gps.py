import RPi.GPIO as GPIO
import requests
import threading
import time
from gps import *

url = "https://remote-shepherd-locations.herokuapp.com/locations/"

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
buzzer=3
GPIO.setup(buzzer,GPIO.OUT)
GPIO.output(buzzer,GPIO.LOW)

class GpsPoller(threading.Thread):

   def __init__(self):
       threading.Thread.__init__(self)
       self.session = gps(mode=WATCH_ENABLE)
       self.current_value = None

   def get_current_value(self):
       return self.current_value

   def run(self):
       try:
            while True:
                self.current_value = self.session.next()
                time.sleep(1) # tune this, you might not get values that quickly
       except StopIteration:
            pass

if __name__ == '__main__':

   gpsp = GpsPoller()
   gpsp.start()
   while 1:
       time.sleep(2)
       GPIO.output(buzzer,GPIO.LOW)
       if 'lat' in gpsp.get_current_value() and 'lon' in gpsp.get_current_value():
           location = {"lat": gpsp.get_current_value().lat, "lon": gpsp.get_current_value().lon}
           json = {"collarId": "113", "lat": gpsp.get_current_value().lat, "lon": gpsp.get_current_value().lon}
           print(location["lat"])
           print(location["lon"]);
           if location["lat"] > 44 and location["lat"] < 48 and location["lon"] > 21 and location["lon"] < 25:
               _ = requests.post(url, json)
               print(_.content.decode("utf-8"))
               if (_.content.decode("utf-8") == "outside_perimeter"):
                   print(_.content.decode("utf-8"))
                   GPIO.output(buzzer,GPIO.HIGH)

