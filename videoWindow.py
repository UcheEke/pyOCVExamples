import cv2

clicked = False

def onMouse(event, x,y,flags,param):
    global clicked
    if event == cv2.EVENT_LBUTTONUP:
        clicked = True

cameraCapture = cv2.VideoCapture(0) # Use the onBoard Camera
cv2.namedWindow('Camera Capture')
cv2.setMouseCallback('Camera Capture',onMouse)

print('Showing camera feed . Click window or press any key to stop')
success, frame = cameraCapture.read()

while success and cv2.waitKey(1) == -1 and not clicked:
    cv2.imshow('Camera Capture', frame)
    success, frame = cameraCapture.read()

cv2.destroyWindow('Camera Capture')
