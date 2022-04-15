import cv2
import numpy as np
import HandTrackinngModule as htm
import time
import autopy
import math


############### ---------------pycaw github -------------##############

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

############### ---------------pycaw github -------------##############

####################  pycaw functions  ################################

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
     IAudioEndpointVolume._iid_, CLSCTX_ALL, None)

volume = cast(interface, POINTER(IAudioEndpointVolume))

# volume.GetMute()
# volume.GetMasterVolumeLevel()

volumeRange = volume.GetVolumeRange()

####################  pycaw functions  ################################

minVolume = volumeRange[0]
maxVolume = volumeRange[1]



def mouse():
     wCam, hCam = 640, 480
     wScr, hScr = autopy.screen.size()
     frameR = 100  # Frame Reduction
     smoothening = 7

     plocX, plocY = 0, 0  # previous location
     clocX, clocY = 0, 0  # current location

     cap = cv2.VideoCapture(0)
     cap.set(3, 640)
     cap.set(4, 480)

     pTime = 0
     cTime = 0

     detector = htm.handDetector()
     lmList = []
     bbox = []

     while True:
          sucess, img = cap.read()

          img = detector.findHands(img)
          lmlist = detector.findPosition(img)

          if (len(lmlist) != 0):
               x1, y1 = lmlist[8][1:]
               x2, y2 = lmlist[12][1:]
               cv2.circle(img, (x1, y1), 15, (0, 0, 0), -1)
               cv2.circle(img, (x2, y2), 15, (0, 0, 0), -1)

               #  Check which fingers are up
               fingers = detector.fingersUp()
               # print(fingers)

               cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)

               # Only Index Finger : Moving Mode
               if fingers[1] == 1 and fingers[2] == 0:
                    # Convert Coordinates
                    x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
                    y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

                    # Smoothen Values
                    clocX = plocX + (x3 - plocX) / smoothening
                    clocY = plocY + (y3 - plocY) / smoothening

                    # Move Mouse
                    autopy.mouse.move(wScr - clocX, clocY)
                    cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                    plocX, plocY = clocX, clocY

               # Both Index and middle fingers are up : Clicking Mode
               if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0:
                    length, img, lineInfo = detector.findDistance(8, 12, img)
                    # print(length)
                    # Click mouse if distance short
                    if length < 40:
                         cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                         autopy.mouse.click()

               # all fingers up then volume control

               if fingers.count(fingers[1]) == len(fingers):
                    # print(lmList)
                    cx1, cy1 = lmlist[4][1], lmlist[4][2]
                    cx2, cy2 = lmlist[8][1], lmlist[8][2]
                    cx, cy = (cx1 + cx2) // 2, (cy1 + cy2) // 2
                    cv2.circle(img, (cx1, cy1), 10, (0, 255, 0), -1)
                    cv2.circle(img, (cx2, cy2), 10, (0, 255, 0), -1)
                    cv2.line(img, (cx1, cy1), (cx2, cy2), (0, 255, 0), 3)

                    # distance between 2 points
                    length = math.hypot(cx2 - cx1, cy2 - cy1)
                    # print(length) # min = 20 max = 150

                    # change range of 20 - 150 in -65 - 0
                    # Here -65 - 0 is rage in function GetVolumeRange range
                    vol = np.interp(length, [20, 150], [minVolume, maxVolume])

                    # function of pycaw to change volume
                    volume.SetMasterVolumeLevel(vol, None)

          cTime = time.time()
          fps = 1 / (cTime - pTime)
          pTime = cTime
          cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 3)

          cv2.imshow("video", img)

          if cv2.waitKey(1) & 0xFF == ord('q'):
               break
