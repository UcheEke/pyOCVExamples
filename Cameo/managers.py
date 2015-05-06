#!/usr/bin/env python

import cv2
import numpy
import time

class CaptureManager(object):
    def __init__(self, capture, previewWindowManager=None, shouldMirrorPreview=False):
        self.previewWindowManager = previewWindowManager
        self.shouldMirrorPreview = shouldMirrorPreview

        self._capture = capture
        self._channel = 0
        self._enteredFrame = False
        self._frame = None
        self._imageFilename = None
        self._videoFilename = None
        self._videoEncoding = None
        self._videoWriter = None

        self._startTime = None
        self._framesElapsed = long(0)
        self._fpsEstimate = None

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self,value):
        if self._channel != value:
            self._channel = value
            self._frame = None

    @property
    def frame(self):
        if self._enteredFrame and self._frame is None:
            _ , self._frame = self._capture.retrieve()
            return self._frame

    @property
    def isWritingImage(self):
        return self._imageFilename is not None

    @property
    def isWritingVideo(self):
        return self._videoFilename is not None

    def enterFrame(self):
        """ Capture the next frame, if any """

        # First, check that any previous frame was exited
        assert not self._enteredFrame, \
            'previous enterFrame() had no matching exitFrame()'

        if self._capture is not None:
            print("[CM] I have a captureObject. Grabbing Frame...")
            self._enteredFrame = self._capture.grab()

    def exitFrame(self):
        """ Draw to the window, write to files, release the frame """

        # Check whether any grabbed frame is retrievable
        # the getter may retrieve and cache the frame
        if self._frame is None:
            print("[CM] I don't have a frame to work on!")
            self._enteredFrame = False
            return

        # Update the fps estimate and related variables
        print("[CM] Updating fps estimate")
        if self._framesElapsed == 0:
            self._startTime = time.time()
        else:
            timeElapsed = time.time() - self._startTime
            self._fpsEstimate = self._framesElapsed / timeElapsed

        print("[CM] Frames elapsed =",self._framesElapsed)
        self._framesElapsed += 1

        # Draw to the window if one exists
        if self.previewWindowManager is not None:
            print("[CM] I have a window manager")
            if self.shouldMirrorPreview: # Do we need to flip image?
                print("[CM] I have to mirror my images")
                mirroredFrame = numpy.fliplr(self._frame).copy()
                self.previewWindowManager.show(mirroredFrame)
            else:
                print("[CM] I don't have to mirror my images")
                self.previewWindowManager.show(self._frame)

        # Write to the image file, if any
        if self.isWritingImage:
            print("[CM] I am writing frame number",self._framesElapsed-1,"to image file", self._imageFilename)
            cv2.imwrite(self._imageFilename, self._frame)
            print("[CM] Setting the filename handle to 'None'")
            self._imageFilename = None # ensure we don't overwrite the current image

        # Write to video if any (carries out an internal check in the call)
        self._writeVideoFrame()

        # Release the frame
        print("[CM] Releasing the frame")
        self._frame = None
        self._enteredFrame = False

    def writeImage(self, filename):
        """ Write the next exited frame to an image file """
        self._imageFilename = filename

    def startWritingVideo(self,filename,encoding=cv2.VideoWriter_fourcc(*'I420')):
        """ Start writing exited frames to a video file """
        self._videoFilename = filename
        self._videoEncoding = encoding

    def stopWritingVideo(self):
        """ Start writing exited frames to a video file """
        self._videoFilename = None
        self._videoEncoding = None
        self._videoWriter = None

    def _writeVideoFrame(self):

        if not self.isWritingVideo:
            print("[CM] No filename supplied for video frames")
            return

        if self._videoWriter is None:
            fps = self._capture.get(cv2.CAP_PROP_FPS)
            if fps == 0.0:
                # The capture's FPS is unknown so use an estimate
                print("[CM] Frame rate is unknown. Estimating...")
                if self._framesElapsed < 20:
                    # Wait until more frames elapse so that the estimate is
                    # more stable
                    return
                else:
                    fps = self._fpsEstimate
                    print("[CM] Frame rate is",self._fpsEstimate)

            size = (int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            print("[CM] image size is", size)
            self._videoWriter = cv2.VideoWriter(
                self._videoFilename, self._videoEncoding,
                fps, size)
            self._videoWriter.write(self,_frame)

class WindowManager(object):

    def __init__(self, windowName, keypressCallback = None, mouseClickCallback = None):
        self.keypressCallback = keypressCallback
        self.mouseClickCallback = mouseClickCallback

        self._windowName = windowName
        self._isWindowCreated = False

    @property
    def isWindowCreated(self):
        return self._isWindowCreated

    @property
    def windowName(self):
        return self._windowName

    def createWindow(self):
        cv2.namedWindow(self._windowName)
        self._isWindowCreated = True

    def show(self, frame):
        print("[WM] Showing frame in window")
        cv2.imshow(self._windowName, frame)

    def destroyWindow(self):
        cv2.destroyWindow(self._windowName)
        self._isWindowCreated = False

    def processEvents(self):
        keycode = cv2.waitKey(1)
        if self.keypressCallback is not None and keycode != -1:
            # Discard any non-ASCII info encoded by GTK
            keycode &= 0xFF
            self.keypressCallback(keycode)

            # Augement this with mousecallback functionality later
