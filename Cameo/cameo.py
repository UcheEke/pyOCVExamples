#!/usr/bin/env python

import cv2
from managers import WindowManager, CaptureManager
import filters


class Cameo(object):

    def __init__(self):
        self._windowManager = WindowManager('Cameo', self.onKeypress)
        self._captureManager = CaptureManager(cv2.VideoCapture(0),
                    self._windowManager, True)
    def run(self):
        """ Run the main loop """

        self._windowManager.createWindow()
        print("Window '{}' Created".format(self._windowManager.windowName))
        print("\n{}\n{}\n{}\n{}".format("Controls:",
                "space   --> Take a screenshot",
                "tab     --> Start/stop recording a screencast",
                "escape  --> Quit"))



        while self._windowManager.isWindowCreated and self._captureManager._framesElapsed < 50:
            self._captureManager.enterFrame()
            frame = self._captureManager.frame
            # Add filtering to the frame
            filters.recolorRGV(frame,frame)
            self._captureManager.exitFrame()
            self._windowManager.processEvents()

    def stop(self):
        print("[CAMEO] closing all processes")
        self._captureManager._capture.release()
        self._windowManager.destroyWindow()


    def onKeypress(self, keycode):

        """ Handle a keypress

        space   --> Take a screenshot
        tab     --> Start/stop recording a screencast
        escape  --> Quit
        """

        if keycode == 32: # Space
            self._captureManager.writeImage('screenshot.png');
            print("Writing image to file....")
        elif keycode == 9: # Tab
            if not self._captureManager.isWritingVideo:
                self._captureManager.startWritingVideo('screencast.avi')
                print("Writing video to file...")
            else:
                self._captureManager.stopWritingVideo()
                print("Stopped writing video")
        elif keycode == 27: # escape
            print("Closing Window...")
            self._windowManager.destroyWindow()

if __name__ == '__main__':
    cameo = Cameo()
