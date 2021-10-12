import numpy as np
import random as rand
from LineModel import LineModel
from material import Material


class Fur:
    """
    Simple class that holds fur data
    """
    def __init__(self, scene, vertices, normals, indices, length=0.1, iterations=3):
        """
        Constructor for fur object
        :param scene: Scene object to add the fur to
        :param vertices: vertices of model to which fur will be added
        :param normals: normals of model to which fur will be added
        :param indices: indices/faces of model to which fur will be added
        :param length: approximate length of the fur
        :param iterations: number of iterations for fur density
        """
        print('Initialising Fur object')

        self.vertices = vertices
        self.indices = indices
        self.scene = scene
        self.length = length
        self.vertices = vertices
        self.normals = normals
        self.iterations = iterations

        self.material = Material(
                Ka=np.array([0.0, 0.0, 0.0], 'f'),
                Kd=np.array([0.5, 0.35, 0.25], 'f'),
                Ks=np.array([0.4, 0.3, 0.25], 'f'),
                Ns=5.0
            )

        self.create_hair()

    def calculate_hair_bulbs(self, hair_vertices, hair_normals, iterations):
        """
        Calculate the coordinates at which extra hairs will start, as well as their directions (normals)
        :param hair_vertices: starting hair vertices
        :param hair_normals: starting hair normals
        :param iterations: hair density iterations
        :return: hair_vertices, hair_normals
        """
        print('Calculating hair bulbs')

        centroids = [[], []]

        if iterations > 0:
            # check if model is built out of triangles or quads
            if self.indices.shape[1] == 3:
                # divide vertices and normals into a list of triangles
                faces_vert = list(self.get_triangles(hair_vertices, self.indices))
                faces_norm = list(self.get_triangles(hair_normals, self.indices))

            elif self.indices.shape[1] == 4:
                # divide vertices and normals into a list of quads
                faces_vert = list(self.get_quads(hair_vertices, self.indices))
                faces_norm = list(self.get_quads(hair_normals, self.indices))

            else:
                print('(E) Model indices not quads or triangles.')
                exit(1)

            # subdivide every face recursively
            for i in range(len(faces_vert)):
                returned_centroids = self.subdivide_faces(faces_vert[i], faces_norm[i], iterations)
                # add returned centroids to list, separated into vertices and normals
                centroids[0] += returned_centroids[0]
                centroids[1] += returned_centroids[1]

            # add newly found vertices and normals to original lists
            hair_vertices = np.concatenate((hair_vertices, centroids[0]))
            hair_normals = np.concatenate((hair_normals, centroids[1]))
            # normalise new normals just in case
            hair_normals /= np.linalg.norm(hair_normals, axis=1, keepdims=True)

        return hair_vertices, hair_normals

    def create_hair(self):
        """
        Create hair line model based on self attributes
        """
        # calculate starting points
        self.hair_vertices, self.hair_normals = self.calculate_hair_bulbs(self.vertices, self.normals, self.iterations)

        # calculate end points
        hair_combined = self.calculate_hair_ends(self.hair_vertices, self.hair_normals, self.length)

        # create normals for every vertex
        all_normals = []
        for i in self.hair_normals:
            all_normals.extend([i, i])

        # create hair model
        self.hair = LineModel(scene=self.scene, vertices=np.array(hair_combined), normals=np.array(all_normals), material=self.material)
        self.hair.bind()
        self.scene.add_model(self.hair)

    def get_triangles(self, vertices, indices):
        """
        Divide vertices list into a list of triangle faces based on indices data
        :param vertices: model vertices
        :param indices: model indices
        :return: triangles list
        """
        triangles = []
        for index in indices:
            triangles.append([vertices[index[0]], vertices[index[1]], vertices[index[2]]])
        return triangles

    def get_quads(self, vertices, indices):
        """
        Divide vertices list into a list of quad faces based on indices data
        :param vertices: model vertices
        :param indices: model indices
        :return: quads list
        """
        quads = []
        for index in indices:
            quads.append([vertices[index[0]], vertices[index[1]], vertices[index[2]], vertices[index[3]]])
        return quads

    def subdivide_faces(self, vertices, normals, n):
        """
        Subdivide face recursively to find more centroids
        :param vertices: triangle or quad vertices
        :param normals: triangle or quad normals
        :param n: iterations
        :return: [vert_centroids, norm_centroids]
        """
        if n == 0:
            return [[], []]

        # if vertices not triangles or quads, print error and abort
        if len(vertices) != 3 and len(vertices) != 4:
            print(
                '(E) Error in Fur.subdivide_faces(): list does not contain 3 or 4 vertices, contains {}.'.format(
                    len(vertices)))
            exit(1)

        # find centroids of face
        vert_centroid = sum(vertices) / len(vertices)
        norm_centroid = sum(normals) / len(normals)

        # randomise position to avoid a visible pattern
        # could randomise in a random direction, but this is sufficient as I don't want to add extra compute time
        diff = vertices[0] - vert_centroid
        vert_centroid += diff * (rand.randint(0, 5) / 10)

        # add to list
        vert_centroids = [vert_centroid]
        norm_centroids = [norm_centroid]

        # if more iterations, create new small triangles with centroid
        if (n - 1) > 0:
            if len(vertices) == 3:
                # if face is a triangle, use original vertices and centroid to create 3 new small triangles
                next_vert = [[vertices[0], vertices[1], vert_centroid],
                             [vertices[0], vertices[2], vert_centroid],
                             [vertices[1], vertices[2], vert_centroid]]
                next_norm = [[normals[0], normals[1], norm_centroid],
                             [normals[0], normals[2], norm_centroid],
                             [normals[1], normals[2], norm_centroid]]
            else:
                # if face is a quad, use original vertices and centroid to create 4 new small triangles
                next_vert = [[vertices[0], vertices[1], vert_centroid],
                             [vertices[1], vertices[2], vert_centroid],
                             [vertices[2], vertices[3], vert_centroid],
                             [vertices[3], vertices[0], vert_centroid]]
                next_norm = [[normals[0], normals[1], norm_centroid],
                             [normals[1], normals[2], norm_centroid],
                             [normals[2], normals[3], norm_centroid],
                             [normals[3], normals[0], norm_centroid]]

            # recursively subdivide each new triangle
            for i in range(len(next_vert)):
                ret = self.subdivide_faces(next_vert[i], next_norm[i], n - 1)
                vert_centroids += ret[0]
                norm_centroids += ret[1]

        return [vert_centroids, norm_centroids]

    def calculate_hair_ends(self, vertices, normals, length, random_angle=False):
        """
        Calculate the end points of each hair line and put into one list with start points
        :param vertices: hair start point vertices
        :param normals: hair normals
        :param length: approximate hair length
        :param random_angle: bool, random hair direction or based on normals?
        :return: hair_combined
        """
        print('Calculating hair ends')

        # pick one normal to use for all hairs if random_angle is True
        index = rand.randint(0, len(normals)-1)
        normal = normals[index]

        hair_combined = []
        # iterate through each hair start point
        for j in range(len(vertices)):
            # random hair length
            hair_length = length * (rand.randint(2, 10) / 10)
            # add hair start point to new list
            hair_combined.append(vertices[j])
            if random_angle:
                # add hair end point based on previously chosen normal
                hair_combined.append((vertices[j] + normal * hair_length))
            else:
                # add hair end point based on the current hair's normal
                hair_combined.append(vertices[j] + normals[j] * hair_length)

        return hair_combined

    def update_density(self, iterations):
        """
        Update the density of the fur
        :param iterations: the new amount of iterations for density
        """
        print('Updating hair density to {} iterations.'.format(iterations))

        # delete old hair model
        self.scene.remove_model(self.hair)
        del self.hair

        self.iterations = iterations

        # create new hair model with new iterations
        self.create_hair()

    def update_length(self, length):
        """
        Update the length of the fur
        :param length: new approximate length
        """
        print('Updating hair length to {}.'.format(length))

        # delete old hair model
        self.scene.remove_model(self.hair)
        del self.hair

        self.length = length

        # create just new hair endings rather than entire hair model from scratch to save compute time
        hair_combined = self.calculate_hair_ends(self.hair_vertices, self.hair_normals, self.length)

        # create normals for every vertex
        all_normals = []
        for i in self.hair_normals:
            all_normals.extend([i, i])

        # create new model with new endings
        self.hair = LineModel(scene=self.scene, vertices=np.array(hair_combined), normals=np.array(all_normals), material=self.material)
        self.hair.bind()
        self.scene.add_model(self.hair)

    def update_rot(self, random_rot):
        """
        Update the direction of the fur to be random
        :param random_rot: bool, random hair rotation or not
        """
        print('Updating hair rotation.')

        # delete old hair model
        self.scene.remove_model(self.hair)
        del self.hair

        # create just new hair endings rather than entire hair model from scratch to save compute time
        hair_combined = self.calculate_hair_ends(self.hair_vertices, self.hair_normals, self.length, random_rot)

        # create normals for every vertex
        all_normals = []
        for i in self.hair_normals:
            all_normals.extend([i, i])

        # create new model with new endings
        self.hair = LineModel(scene=self.scene, vertices=np.array(hair_combined), normals=np.array(all_normals), material=self.material)
        self.hair.bind()
        self.scene.add_model(self.hair)
