import cv2
import numpy
import utils

def recolorRC(src, dst):
    """ Simulate conversion from BGR to RC (red, cyan).

    The source and destination images must both be in BGR format
    Blues and greens are replaced with cyans by averaging the two
    channels and applying the average to both

    Pseudocode:
    dst.b = dst.g = 0.5*(src.b + src.g)
    dst.r = src.r

    """
    b,g,r = cv2.split(src)
    cv2.addWeighted(b,0.5,g,0.5,0,b)
    cv2.merge((b,b,r),dst)


def recolorRGV(src, dst):
    """ Simulate conversion from BGR to RGV (red, green, value)

    The source and destination images must both be in BGR format

    Blues are desaturated
    dst.b = min(src.b, src.g, src.r)
    dst.g = src.g
    dst.r = src.r

    """

    b,g,r = cv2.split(src)
    cv2.min(b,g,b)
    cv2.min(b,r,b)
    cv2.merge((b,g,r),dst)

def recolorCMV(src,dst):
    """ Simulate conversion from BGR to CMV (Cyan, Magenta, value)

    Yellows are desaturated.
    dst.b = max(src.b,src.g,src.r)
    dst.g = src.g
    dst.r = src.r
    """

    b,g,r = cv2.split(src)
    cv2.max(b,g,b)
    cv2.max(b,r,b)
    cv2.merge((b,g,r),dst)


def strokeEdges(src,dst,blurKsize=7,edgeKsize=5):
    if blurKsize >= 3:
        blurredSrc = cv2.medianBlur(src, blurKsize)
        graySrc = cv2.cvtColor(blurredSrc,cv2.COLOR_BGR2GRAY)
    else:
        graySrc =cv2.cvtColor(src,cv2.COLOR_BGR2GRAY)
    cv2.Laplacian(graySrc,cv2.CV_8U,graySrc,ksize=edgeKsize)
    normalizedInverseAlpha = (1.0 / 255) * (255 - graySrc)
    channels = cv2.split(src)
    for channel in channels:
        channel[:] = channel * normalizedInverseAlpha
    cv2.merge(channels, dst)



class VFuncFilter(object):
    """ A Filter that applies a function to V (or all of BGR) """

    def __init__(self, vFunc = None, dtype = numpy.uint8):
        length = numpy.iinfo(dtype).max + 1
        self._vLookupArray = utils.createLookupArray(vFunc,length)

    def apply(self, src, dst):
        """ Apply the filter with a BGR or gray source/destination."""
        srcFlatView = utils.flatView(src)
        dstFlatView = utils.flatView(dst)
        utils.applyLookupArray(self._vLookupArray, srcFlatView, dstFlatView)

class VCurveFilter(VFuncFilter):
    """ A filter that applies a curve to V (or all of BGR)
        Extends the VFuncFilter class
        """
    def __init__(self, vPoints, dtype = numpy.uint8):
        VFuncFilter.__init__(self, utils.createCurveFunc(vPoints),dtype)

class BGRFuncFilter(object):
    """ A filter that applies different functions to each of BGR """

    def __init__(self,vFunc=None,bFunc=None,gFunc=None,rFunc=None,dtype=numpy.uint8):
        length = numpy.iinfo(dtype).max + 1
        print("length parameter:",length)
        self._bLookupArray = utils.createLookupArray(
            utils.createCompositeFunc(bFunc,vFunc),length)
        self._gLookupArray = utils.createLookupArray(
            utils.createCompositeFunc(gFunc,vFunc),length)
        self._rLookupArray = utils.createLookupArray(
            utils.createCompositeFunc(rFunc,vFunc),length)

    def apply(self, src, dst):
        """ Apply the filter with a BGR source/destination"""
        b,g,r = cv2.split(src)
        utils.applyLookupArray(self._bLookupArray,b,b)
        utils.applyLookupArray(self._gLookupArray,g,g)
        utils.applyLookupArray(self._rLookupArray,r,r)
        cv2.merge((b,g,r), dst)

class BGRCurveFilter(BGRFuncFilter):
    """ A filter that applies different curves to each of v,b,g and r """
    def __init__(self, vPoints=None,bPoints=None,gPoints=None,rPoints=None,
            dtype=numpy.uint8):
        BGRFuncFilter.__init__(self,
                utils.createCurveFunc(vPoints),
                utils.createCurveFunc(bPoints),
                utils.createCurveFunc(gPoints),
                utils.createCurveFunc(rPoints),
                dtype)

class BGRPortraCurveFilter(BGRCurveFilter):
    """ Emulation of the Kodak Portra like curves """

    def __init__(self, dtype=numpy.uint8):
        BGRCurveFilter.__init__(
        self,
        vPoints = [(0,0),(23,20),(157,173),(255,255)],
        bPoints = [(0,0),(41,46),(231,228),(255,255)],
        gPoints = [(0,0),(52,47),(189,196),(255,255)],
        rPoints = [(0,0),(69,69),(213,218),(255,255)],
        dtype = dtype)

class BGRProviaCurveFilter(BGRCurveFilter):
    """ Emulates the Fuji Provia-like curves on BGR """

    def __init__(self, dtype=numpy.uint8):
        BGRCurveFilter.__init__(
        self,
        bPoints = [(0,0),(35,25),(205,227),(255,255)],
        gPoints = [(0,0),(27,21),(196,207),(255,255)],
        rPoints = [(0,0),(59,54),(202,210),(255,255)],
        dtype = dtype)

class BGRVelviaCurveFilter(BGRCurveFilter):
    """ Emulates the Fuji Velvia curves on BGR """

    def __init__(self, dtype=numpy.uint8):
        BGRCurveFilter.__init__(
        self,
        vPoints = [(0,0),(128,118),(221,215),(255,255)],
        bPoints = [(0,0),(25,21),(122,153),(165,206),(255,255)],
        gPoints = [(0,0),(25,21),(95,102),(181,208),(255,255)],
        rPoints = [(0,0),(41,28),(183,209),(255,255)],
        dtype = dtype)

class BGRCrossProcessCurveFilter(BGRCurveFilter):
    """ Emulates the Cross-process-like curves on BGR """

    def __init__(self, dtype=numpy.uint8):
        BGRCurveFilter.__init__(
        self,
        bPoints = [(0,20),(255,255)],
        gPoints = [(0,0),(56,39),(208,226),(255,255)],
        rPoints = [(0,0),(56,22),(211,255),(255,255)],
        dtype = dtype)

class VConvolutionFilter(object):
    """ A filter that applies a convolution to V (or all of BGR) """

    def __init__(self, kernel):
        """ The kernel is a numpy array of odd length whose center element represents the
            pixel of interest. It is altered according to the weights of all the surrounding
            elements """
        self._kernel = kernel

    def apply(self, src, dst):
        """ Apply the given filter with a BGR or Grayscale src/destination """
        cv2.filter2D(src,-1, self._kernel, dst)

class SharpenFilter(VConvolutionFilter):
    """ A specific case of VConvolution Filter where the kernel's center output is 9x the value of
        its input -1 from the value of each of the surrounding pixels. This amplifies contrasts between
        differing colors in the src material. """

    def __init__(self):
        kernel = numpy.array([[-1,-1,-1],
                              [-1, 9,-1],
                              [-1,-1,-1]])
        VConvolutionFilter.__init__(self,kernel)

class FindEdgesFilter(VConvolutionFilter):
    """ The sum of the weights in this particular filter is 0. This turns edges white and non edges black
        """
    def __init__(self):
        kernel = numpy.array([[-1,-1,-1],
                              [-1, 8,-1],
                              [-1,-1,-1]])
        VConvolutionFilter.__init__(self, kernel)

class BlurFilter(VConvolutionFilter):
    """ For a blur effect, the weights should sum to one and should be positive throughout the neighbourhood
        """
    def __init__(self):
        """ Define a blur kernel with a 2-pixel radius """
        kernel = numpy.array([[0.04,0.04,0.04,0.04,0.04],
                              [0.04,0.04,0.04,0.04,0.04],
                              [0.04,0.04,0.04,0.04,0.04],
                              [0.04,0.04,0.04,0.04,0.04],
                              [0.04,0.04,0.04,0.04,0.04]])
        VConvolutionFilter.__init__(self, kernel)

# Removing the symmetry from the kernels produces some nice effects

class EmbossFilter(VConvolutionFilter):
    """ An emboss filter with a 1-pixel radius """

    def __init__(self):
        kernel = numpy.array([[-2,-1, 0],
                              [-1, 8, 1],
                              [ 0, 1, 2]])
        VConvolutionFilter.__init__(self, kernel)
