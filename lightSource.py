import numpy as np


class LightSource:
    """
    Class for a light source
    """

    def __init__(self, scene, position=[2., 2., 0.], Ia=[1.0, 1.0, 1.0], Id=[1.0, 1.0, 1.0], Is=[1.0, 1.0, 1.0]):
        """
        Initialise the light source
        :param scene: scene to which light source will be added
        :param position: the position of the light source
        :param Ia: ambient illumination
        :param Id: diffuse illumination
        :param Is: specular illumination
        """
        self.position = np.array(position, 'f')
        self.Ia = Ia
        self.Id = Id
        self.Is = Is
