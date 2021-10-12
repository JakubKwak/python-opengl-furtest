from OpenGL.GL import *
from matutils import *
import numpy as np
from material import Material


class BaseModel:
    """
    Base class for all models, implementing the basic draw function for triangular meshes
    Based on class from workshops
    """

    def __init__(self, scene, M=poseMatrix(), color=[1., 1., 1.], primitive=GL_TRIANGLES, visible=True):
        """
        Initialise model data
        :param scene: scene to which add the model
        :param M: position of the model
        :param color: color of the model
        :param primitive: primitive type (EG. GL_TRIANGLES)
        :param visible: visibility of the model
        """

        print('Initialising {}'.format(self.__class__.__name__))

        # assign constructor variables to object attributes
        self.visible = visible
        self.scene = scene
        self.primitive = primitive
        self.color = color
        self.M = M

        # define other attributes
        self.vertices = None
        self.indices = None
        self.normals = None
        self.vertex_colors = None
        self.vbos = {}
        self.attributes = {}

        # define default material
        self.material = Material(
            Ka=np.array([0.1, 0.1, 0.2], 'f'),
            Kd=np.array([0.1, 0.5, 0.1], 'f'),
            Ks=np.array([0.9, 0.9, 1.0], 'f'),
            Ns=10.0
        )

    def initialise_vbo(self, name, data):
        """
        Initalise VBO for specific attribute
        :param name: name of the attribute in GLSL shader
        :param data: attribute data
        :return:
        """
        print('Initialising VBO for attribute {}'.format(name))

        # bind the location of the attribute in the GLSL program to the next index
        self.attributes[name] = len(self.vbos)

        # if data is empty, then print warning and abort
        if data is None:
            print('(W) Warning in {}.bind_attribute(): Data array for attribute {} is None'.format(
                self.__class__.__name__, name))
            return

        # create a buffer object
        self.vbos[name] = glGenBuffers(1)
        # bind it
        glBindBuffer(GL_ARRAY_BUFFER, self.vbos[name])

        # set the data in the buffer as the vertex array
        glBufferData(GL_ARRAY_BUFFER, data, GL_STATIC_DRAW)

        # enable the attribute
        glEnableVertexAttribArray(self.attributes[name])

        # associate the bound buffer tp the corresponding input location in the shader
        glVertexAttribPointer(index=self.attributes[name], size=data.shape[1], type=GL_FLOAT, normalized=False,
                              stride=0, pointer=None)

    def bind(self):
        """
        Store vertex data in VBO to upload to GPU at render time
        """

        # use a vertex array object to pack all buffers for rendering in the GPU
        self.vao = glGenVertexArrays(1)

        # bind the VAO to retrieve all buffers and rendering context
        glBindVertexArray(self.vao)

        if self.vertices is None:
            print('(W) Warning in {}.bind(): No vertex array!'.format(self.__class__.__name__))

        # initialise VBOs and link to shader program attributes
        self.initialise_vbo('position', self.vertices)
        self.initialise_vbo('normal', self.normals)

        # if indices are provided, put them in a buffer too
        if self.vertices is not None:
            self.index_buffer = glGenBuffers(1)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices, GL_STATIC_DRAW)

        # bind all attributes to the correct locations in the VAO
        for name in self.attributes:
            glBindAttribLocation(self.scene.shaders.program, self.attributes[name], name)
            print('Binding attribute {} to location {}'.format(name, self.attributes[name]))

        # unbind the VAO and VBO when done to avoid any side effects
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def draw(self, Mp, shaders):
        """
        Draw the model using OpenGL
        :param Mp: position matrix
        :param shaders: shaders to use
        """

        if self.visible:
            if self.vertices is None:
                print('(W) Warning in {}.draw(): No vertex array!'.format(self.__class__.__name__))

            # tell openGL to use this shader program for rendering
            glUseProgram(shaders.program)

            # setup the shader program and give it the model, view and projection matrices to use for rendering
            shaders.bind(
                P=self.scene.P,
                V=self.scene.camera.V,
                M=np.matmul(Mp, self.M),
                mode=self.scene.mode,
                material=self.material,
                light=self.scene.light
            )

            # bind the VAO so that all buffers are bound correctly and the following operations affect them
            glBindVertexArray(self.vao)

            # check whether the data is stored as vertex array or index array
            if self.indices is not None:
                # draw the data in buffer using index array
                glDrawElements(self.primitive, self.indices.flatten().shape[0], GL_UNSIGNED_INT, None)
            else:
                # draw the data in buffer using vertex array ordering only
                glDrawArrays(self.primitive, 0, self.vertices.shape[0])

            # unbind the shader to avoid side effects
            glBindVertexArray(0)


def __del__(self):
    """
    Release all VBO objects when finished
    """
    for vbo in self.vbos.items():
        glDeleteBuffers(1, vbo)
