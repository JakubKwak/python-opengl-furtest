from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from matutils import *


class Camera:
    """
    Base class for the camera
    """

    def __init__(self, size):
        """
        Constructor for camera
        :param size: window size
        """
        self.size = size
        self.V = np.identity(4)
        self.V[2, 3] = -5.0  # translate the camera five units back, looking at the origin
        self.phi = 0.
        self.psi = 0.
        self.distance = 5.
        self.center = [0., 0., 0.]

    def update(self):
        """
        Update the camera
        """
        T0 = translationMatrix(self.center)
        R = np.matmul(rotationMatrixX(self.psi), rotationMatrixY(self.phi))
        T = translationMatrix([0., 0., -self.distance])
        self.V = np.matmul(np.matmul(T, R), T0)#################################################################################