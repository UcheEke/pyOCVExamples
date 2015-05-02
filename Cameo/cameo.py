#!/usr/bin/env python

import cv2
from managers import WindowManager, CaptureManager


class Cameo(object):

    def __init__(self):
        self._windowManager = WindowManager('Cameo', self.onKeypress)
        self._captureManager = CaptureManager(cv2.VideoCapture(0),
                    self._windowManager, True)
        self.shotIndex = 0;
        self.castIndex = 0;

    def run(self):
        """ Run the main loop """

        self._windowManager.createWindow()
        print("Window '{}' Created".format(self._windowManager.windowName))
        print("\n{}\n{}\n{}\n{}".format("Controls:",
                "space   --> Take a screenshot",
                "tab     --> Start/stop recording a screencast",
                "escape  --> Quit"))

        while self._windowManager.isWindowCreated:
            self._captureManager.enterFrame()
            frame = self._captureManager.frame

            # TODO Filter the frame!!

            self._captureManager.exitFrame()
            self._windowManager.processEvents()

    def onKeypress(self, keycode):

        """ Handle a keypress

        space   --> Take a screenshot
        tab     --> Start/stop recording a screencast
        escape  --> Quit
        """

        if keycode == 32: # Space
            self._captureManager.writeImage('screenshot('+ str(self.shotIndex) + ').png');
            self.shotIndex += 1
        elif keycode == 9: # Tab
            if not self._captureManager.isWritingVideo:
                self._captureManager.startWritingVideo('screencast(' + str(self.castIndex) + ').avi')
                self.castIndex += 1
            else:
                self._captureManager.stopWritingVideo()
        elif keycode == 27: # escape
            self._windowManager.destroyWindow()


if __name__ == '__main__':
    cameo = Cameo()
    cameo.run()
