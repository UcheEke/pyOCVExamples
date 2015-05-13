import cv2
import numpy
import scipy.interpolate


def createCurveFunc(points):
    """ Return a function derived from control points """
    if points is None:
        return None

    numPoints = len(points)
    if numPoints < 2: # You need at least 2 points!
        return None

    xs, ys = zip(*points)
    if numPoints < 4:
        kind = 'linear'
    else:
        kind = 'cubic'

    return scipy.interpolate.interp1d(xs, ys, kind, bounds_error = False)

# Because the previous function may be expensive if performed on each pixel of each frame
# and there are only a possible 256 values in an 8-bit channel, we can create a lookup table

def createLookupArray(func, length=256):
    """ return a lookup for whole-number inputs to a function

    The lookup values are clamped to [0,length-1]
    """

    if func is None:
        return None
    lookupArray = numpy.empty(length)

    i = 0
    while i < length:
        func_i = func(i)
        lookupArray[i] = min(max(0,func_i),length-1)
        i += 1
    return lookupArray

def applyLookupArray(lookupArray, src, dst):
     """ Map a source to a destination using a lookup """
     if lookupArray is None:
         return None
     dst[:] = lookupArray[src]

def createCompositeFunc(func0, func1):
    """ Return a composite of two functions (which take only a single argument each) """
    if func0 is None:
        return func1
    if func1 is None:
        return func0
    return lambda x: func0(func1(x))

def createFlatView(array):
    """ Return a 1D view of an array of any dimensionality """
    flatView = array.view()
    flatView.shape = array.size
    return flatView

def isGray(image):
    """ Returns True if the image has only one channel per pixel """
    return image.ndim < 3

def widthHeightDividedBy(image, divisor):
    """ return an image's dimensions divided by a value """

    h, w = image.shape[:2]
    return (w/divisor, h/divisor)
