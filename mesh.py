from material import Material
import numpy as np

class Mesh:
    """
    Simple class that holds mesh data
    """
    def __init__(self, vertices, faces=None, normals=None, material=Material()):
        """
        Initialise mesh object
        :param vertices: mesh vertices
        :param faces: mesh faces
        :param normals: mesh normals
        :param material: mesh material
        """

        # assign arguments to attributes
        self.vertices = vertices
        self.faces = faces
        self.material = material

        print('Creating mesh')
        print('- {} vertices, {} faces'.format(self.vertices.shape[0], self.faces.shape[0]))
        print('- {} vertices per face'.format(self.faces.shape[1]))
        print('- vertices ID in range [{},{}]'.format(np.min(self.faces.flatten()), np.max(self.faces.flatten())))

        if normals is None:
            if faces is None:
                print(
                    '(W) Warning: the current code only calculates normals using the face vector of indices, which was not provided here.')
            else:
                self.calculate_normals()
        else:
            self.normals = normals

    def calculate_normals(self):
        """
        Calculate normals from mesh faces
        """

        self.normals = np.zeros((self.vertices.shape[0], 3), dtype='f')

        for f in range(self.faces.shape[0]):
            # calculate the face normal using cross product of triangle sides
            a = self.vertices[self.faces[f, 1]] - self.vertices[self.faces[f, 0]]
            b = self.vertices[self.faces[f, 2]] - self.vertices[self.faces[f, 0]]
            face_normal = np.cross(a, b)

            # blend normal on all 3 vertices
            for j in range(3):
                self.normals[self.faces[f, j], :] += face_normal

        # normalise the vectors
        self.normals /= np.linalg.norm(self.normals, axis=1, keepdims=True)
