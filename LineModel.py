from OpenGL.GL import *
from matutils import *
import numpy as np
from BaseModel import BaseModel
from material import Material


class LineModel(BaseModel):
    """
    Basic class for creating line models, child of BaseModel
    """
    def __init__(self, scene, vertices, normals, M=poseMatrix(), material=None, primitive=GL_LINES, visible=True):
        """
        Initialise the model data
        :param scene: scene to which model will be added
        :param vertices: vertices of hair model
        :param normals: normals of hair model
        :param M: position of model
        :param primitive: line primitive type (EG. GL_LINES, GL_LINE_STRIP)
        :param visible: model visibility
        """

        # assign constructor arguments to object attributes
        self.visible = visible
        self.vertices = vertices
        self.scene = scene
        self.primitive = primitive
        self.M = M
        self.material = material
        self.normals = normals

        # define other attributes
        self.indices = None
        self.vertex_colors = None  # not needed for lines
        self.vbos = {}
        self.attributes = {}

        if self.material is None:
            # default material if none given
            self.material = Material(
                Ka=np.array([0.0, 0.0, 0.0], 'f'),
                Kd=np.array([0.5, 0.5, 0.5], 'f'),
                Ks=np.array([0.9, 0.9, 1.0], 'f'),
                Ns=10.0
            )


def __del__(self):
    """
    Release all VBO objects when finished.
    """
    for vbo in self.vbos.items():
        glDeleteBuffers(1, vbo)