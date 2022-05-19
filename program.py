from sense_hat import SenseHat
import time
from time import sleep
import requests
import threading
from socket import *
import datetime
import math
import json

sense = SenseHat()
sense.low_light = True

BROADCAST_TO_PORT = 10100
socket = socket(AF_INET, SOCK_DGRAM)
#socket.bind(('', 14593))     # (ip, port)
# no explicit bind: will bind to default IP + random port
socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

g = (0, 255, 0)
n = (0, 0, 0)
r = (255, 0, 0)
y = (255,255,0)

idleLCD = [
    n, n, n, n, n, n, n, n,
    n, n, n, n, n, n, n, n,
    n, n, n, y, y, n, n, n,
    n, n, n, y, y, n, n, n,
    n, n, n, y, y, n, n, n,
    n, n, n, y, y, n, n, n,
    n, n, n, n, n, n, n, n,
    n, n, n, n, n, n, n, n
]

sentLCD = [
    n, n, n, n, n, n, n, n,
    n, n, n, n, n, n, g, n,
    n, n, n, n, n, g, g, n,
    n, n, n, n, n, g, n, n,
    n, n, g, n, n, g, n, n,
    n, n, n, g, g, n, n, n,
    n, n, n, g, g, n, n, n,
    n, n, n, n, n, n, n, n
]

errLCD = [
    n, n, n, n, n, n, n, n,
    n, r, n, n, n, n, r, n,
    n, n, r, n, n, r, n, n,
    n, n, n, r, r, n, n, n,
    n, n, n, r, r, n, n, n,
    n, n, r, n, n, r, n, n,
    n, r, n, n, n, n, r, n,
    n, n, n, n, n, n, n, n
]

#create class with attribute to enable/support multi threading
class lcdManager():
  lcdShowGood = False
  lcdShowBad = False
        
  def startThread(self):
    threadLCD = threading.Thread(target=run)
    threadLCD.start()

def run():
  alternate = True
  while True:
    if threadLCD.lcdShowGood == True:
      sense.set_rotation(0)
      alternate = True
      sense.set_pixels(sentLCD)
      time.sleep(2)
      threadLCD.lcdShowGood = False

    if threadLCD.lcdShowBad == True:
      sense.set_rotation(0)
      alternate = True
      sense.set_pixels(errLCD)
      
    if (threadLCD.lcdShowGood == False) and (threadLCD.lcdShowBad == False):
      if alternate == True:
        sense.set_rotation(0)
        sense.set_pixels(idleLCD)
        alternate = False
      else:
        sense.set_rotation(90)
        sense.set_pixels(idleLCD)
        alternate = True
      time.sleep(0.75)


def getAccel():
  #get data from sensor and bind to xyz
  acceleration = sense.get_accelerometer_raw()
  x = acceleration['x']
  y = acceleration['y']
  z = acceleration['z']

  #abs converts negative values to positive
  x=abs(x)
  y=abs(y)
  z=abs(z)
    
  #get total acceleration
  return math.sqrt(x**2 + y**2 + z**2)

def sendData(accel):
  threadLCD.lcdShowGood = True
  #format string to datetime and manipulates format for C# library
  dateString = str(datetime.datetime.now())
  dateString = dateString.replace(" ","T")
      
  dataJSON = {
    "id":0,
    "speed":accel,
    "dateTimeNow": dateString
  }
      
  #convert python dictionary object to JSON for the 'dumb' UDP server
  dataPacket = json.dumps(dataJSON)
      
  #sends packet to UDP server and prints it in internal log
  socket.sendto(bytes(str(dataPacket), "UTF-8"), ('<broadcast>', BROADCAST_TO_PORT))
  print(str(dataPacket))
  time.sleep(2)

def mainLoop():
  lastTime=0
  while True:
    threadLCD.lcdShowBad = False
    accel = getAccel()
    
    if accel > 3:
      maxReached=0
      print("Throw registered")
      time.sleep(3)
      while maxReached < 10:
        print("Ball flying")
        accel = getAccel()
        threadLCD.lcdShowBad = True
        if accel > 3:
          #use accel deltas
          print("Data should send")
          sendData(accel)
          threadLCD.lcdShowBad = False
          maxReached=2000 #kill while loop
        if time.time() > lastTime+1:
          maxReached = maxReached+1
          lastTime = time.time()
      


#initialize object for class lcdManager
threadLCD = lcdManager()
#starts the object
threadLCD.startThread()
mainLoop()