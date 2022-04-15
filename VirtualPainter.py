import cv2
import mediapipe as mp
import time
import os
import VirtualMouse as vm
import numpy as np
import HandTrackinngModule as htm

def paint():
    folderPath = "virtual paint design"
    myList = os.listdir(folderPath)

    # print(myList)
    overlayList = []
    for imPath in myList:
        image = cv2.imread(f'{folderPath}/{imPath}')
        overlayList.append(image)
    # print(len(overlayList))

    header = overlayList[0]
    drawColor = (0, 255, 0)
    xp, yp = 0, 0
    brushThickness = 15
    eraserThickness = 25
    imgCanvas = np.zeros((540, 960, 3), np.uint8)
    imgCanvas1 = np.zeros((540, 960, 3), np.uint8) + 255

    cap = cv2.VideoCapture(0)
    cap.set(3, 960)

    detector = htm.handDetector(detectionConfidence=0.65, numberOfHands=1)

    while True:
        sucess, img = cap.read()
        img = cv2.flip(img, 1)
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=False)
        # print(lmList)

        if len(lmList) != 0:

            # tip of index and middle fingers
            x1, y1 = lmList[8][1:]
            x2, y2 = lmList[12][1:]

            # 3. Check which fingers are up
            fingers = detector.fingersUp()
            # print(fingers)

            # 4. If Selection Mode - Two finger are up
            if fingers[1] and fingers[2]:
                # print("Selection Mode")
                xp, yp = 0, 0
                if y1 < 94:
                    if 190 < x1 < 320:
                        header = overlayList[0]
                        drawColor = (0, 255, 0)
                    elif 335 < x1 < 475:
                        header = overlayList[1]
                        drawColor = (255, 0, 0)
                    elif 490 < x1 < 635:
                        header = overlayList[2]
                        drawColor = (0, 0, 255)
                    elif 660 < x1 < 820:
                        header = overlayList[3]
                        drawColor = (0, 0, 0)
                    elif 840 < x1 < 950:
                        header = overlayList[4]
                        cap.release()
                        cv2.destroyAllWindows()
                        vm.mouse()
                        # drawColor = (0, 0, 0)

            # 5. If Drawing Mode - Index finger is up
            if fingers[1] and fingers[2] == False:
                cv2.circle(img, (x1, y1), 15, drawColor, cv2.FILLED)
                # print("Drawing Mode")

                if xp == 0 and yp == 0:
                    xp, yp = x1, y1

                cv2.line(img, (xp, yp), (x1, y1), drawColor, brushThickness)
                if drawColor == (0, 0, 0):
                    cv2.line(img, (xp, yp), (x1, y1), drawColor, eraserThickness)
                    cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, eraserThickness)
                    cv2.line(imgCanvas1, (xp, yp), (x1, y1), (255, 255, 255), eraserThickness)

                else:
                    cv2.line(img, (xp, yp), (x1, y1), drawColor, brushThickness)
                    cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brushThickness)
                    cv2.line(imgCanvas1, (xp, yp), (x1, y1), drawColor, brushThickness)

                xp, yp = x1, y1

        imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
        _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
        imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and(img, imgInv)
        img = cv2.bitwise_or(img, imgCanvas)

        img[0:94, 0:960] = header

        cv2.imshow("Result", img)
        # cv2.imshow("Canvas", imgCanvas1)
        # cv2.imshow("Inv", imgInv)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            cv2.imwrite("E:/College/Opencv/Projects/VirtualMousePaint/save.jpg", imgCanvas1)
            cv2.rectangle(img, (0, 200), (img.shape[1], 300), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, "Saved", (400, 270), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 0, 255), 2)
            cv2.imshow("Result", img)
            cv2.waitKey(500)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == "__main__":
    paint()