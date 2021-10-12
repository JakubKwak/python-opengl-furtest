from scene import Scene
from blender import load_obj_file
from LineModel import *
from fur import Fur
import numpy as np

class DrawModelFromMesh(BaseModel):
    """
    Class for model drawn from mesh
    """

    def __init__(self, scene, M, mesh):
        """
        Initalise the model data
        :param scene: scene to which model will be added
        :param M: position of the model
        :param mesh: mesh to draw model from
        """

        BaseModel.__init__(self, scene=scene, M=M)

        # initialise the vertices of the shape
        self.vertices = mesh.vertices

        # initialise the faces of the shape
        self.indices = mesh.faces

        # check which primitives we need to use for drawing
        if self.indices.shape[1] == 3:
            self.primitive = GL_TRIANGLES
        elif self.indices.shape[1] == 4:
            self.primitive = GL_QUADS
        else:
            print(
                '(E) Error in DrawModelFromObjFile.__init__(): index array must have 3 (triangles) or 4 (quads) columns, found {}!'.format(
                    self.indices.shape[1]))
            raise

        # initialise the normals per vertex
        self.normals = mesh.normals

        # save material information
        self.material = mesh.material

        # default vertex colors to white
        self.vertex_colors = np.ones((self.vertices.shape[0], 3), dtype='f')

        # create zero normals if none provided
        if self.normals is None:
            print('(W) No normal array was provided.')
            print('--> setting to zero.')
            self.normals = np.zeros(self.vertices.shape, dtype='f')

        # create fur for model and add to scene
        fur = Fur(scene, self.vertices, self.normals, self.indices)
        self.scene.set_fur(fur)

        # bind the data to a vertex array
        self.bind()


"""
Main code to run program
"""
if __name__ == '__main__':
    # initialises the scene
    scene = Scene()

    #
    # MODEL SELECTION
    #
    meshes = load_obj_file('models/torus.obj')  # change to 'models/torus.obj' for torus model

    # add imported models to scene
    scene.add_models_list(
        [DrawModelFromMesh(scene=scene, M=poseMatrix(), mesh=mesh) for mesh in meshes]
    )

    # start drawing
    scene.run()


