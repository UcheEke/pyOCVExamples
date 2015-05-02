import cv2

cv_width  = cv2.CAP_PROP_FRAME_WIDTH
cv_height = cv2.CAP_PROP_FRAME_HEIGHT

videoCapture = cv2.VideoCapture(0)
fps = 10
print("Current Frame Rate: ", fps)

size = (int(videoCapture.get(cv_width)),int(videoCapture.get(cv_height)))
print("Capture size: ", size)

videoWriter = cv2.VideoWriter('MyOutputVid.avi',cv2.VideoWriter_fourcc('I','4','2','0'),fps,size)

success, frame = videoCapture.read()
num_frames_remaining = 10 * fps - 1

while success and num_frames_remaining > 0:
    videoWriter.write(frame)
    success,frame = videoCapture.read()
    num_frames_remaining -= 1
