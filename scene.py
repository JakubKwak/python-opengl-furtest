import pygame
from OpenGL.GL import *
from shaders import Shaders,Uniform
from camera import Camera
from matutils import *
from lightSource import LightSource


class Scene:
    """
    Main class for drawing an OpenGL scene using PyGame library
    """
    def __init__(self, width=800, height=600):
        """
        Initialise the scene
        :param width: window width
        :param height: window height
        """
        # set window size
        self.window_size = (width, height)

        # initialise the pygame window, 30 fps
        pygame.init()
        screen = pygame.display.set_mode(self.window_size, pygame.OPENGL | pygame.DOUBLEBUF, 30)

        # start initialising window from OpenGL side
        glViewport(0, 0, self.window_size[0], self.window_size[1])
        # set background color
        glClearColor(0.5, 0.5, 1.0, 1.0)

        # enable back face culling
        glEnable(GL_CULL_FACE)

        # enable vertex array capability
        glEnableClientState(GL_VERTEX_ARRAY)

        # enable depth test
        glEnable(GL_DEPTH_TEST)

        # dictionary of shaders used in this scene
        self.shaders_list = {
            'Gouraud': Shaders('gouraud'),
        }

        # compile shaders
        for shader in self.shaders_list.values():
            shader.compile()

        self.shaders = self.shaders_list['Gouraud']

        # initialise the projective transform
        near = 1.5
        far = 20
        left = -1.0
        right = 1.0
        top = -1.0
        bottom = 1.0

        # use orthographic projection
        self.P = frustumMatrix(left, right, top, bottom, near, far)

        # initialise camera
        self.camera = Camera(self.window_size)

        # initialise the light
        self.light = LightSource(self, position=[5., 5., 5.])

        # full interpolated rendering mode for shaders
        self.mode = 6

        self.models = []

        self.fur = None

    def add_model(self, model):
        """
        Add model to model list
        :param model: model to add
        """
        self.models.append(model)

    def add_models_list(self,models_list):
        """
        Add lists of models to model list
        :param models_list: list of models to add
        """
        self.models.extend(models_list)

    def remove_model(self, model):
        """
        Remove model from model list
        :param model: model to remove
        """
        self.models.remove(model)

    def draw(self):
        """
        Draw all models
        """

        # clear the scene and depth buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # update the camera
        self.camera.update()

        # iterate through models and draw them
        for model in self.models:
            model.draw(Mp=poseMatrix(), shaders=self.shaders)

        # flip buffers to display the frame
        pygame.display.flip()

    def set_fur(self, fur):
        """
        Set the fur object
        :param fur: for object
        """
        self.fur = fur

    def keyboard(self, event):
        """
        Keyboard events
        :param event: current keyboard event
        """
        if event.key == pygame.K_q:
            # if Q, then quit
            self.running = False
        elif event.key == pygame.K_l and self.fur is not None:
            # if L, increase fur length
            length = self.fur.length + 0.01
            # upper limit
            if length <= 1:
                self.fur.update_length(length)
        elif event.key == pygame.K_k and self.fur is not None:
            # if K, decrease fur length
            length = self.fur.length - 0.01
            # lower limit
            if length >= 0.02:
                self.fur.update_length(length)
        elif event.key == pygame.K_m and self.fur is not None:
            # if M, increase fur density
            iterations = self.fur.iterations + 1
            # upper limit
            if iterations <= 10:
                self.fur.update_density(iterations)
        elif event.key == pygame.K_n and self.fur is not None:
            # if N, decrease fur density
            iterations = self.fur.iterations - 1
            #  lower limit
            if iterations >= 0:
                self.fur.update_density(iterations)
        elif event.key == pygame.K_b and self.fur is not None:
            # if B, move fur
            self.fur.update_rot(True)
        elif event.key == pygame.K_v and self.fur is not None:
            # if V, reset fur
            self.fur.update_rot(False)

    def pygameEvents(self):
        """
        PYGame events
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # check whether the window has been closed
                self.running = False
            elif event.type == pygame.KEYDOWN:
                # if keyboard event, run keyboard events function
                self.keyboard(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # mouse scroll wheel event
                if event.button == 4:
                    # scroll up, zoom in
                    self.camera.distance = max(1, self.camera.distance - 1)
                elif event.button == 5:
                    # scroll down, zoom out
                    self.camera.distance += 1
            elif event.type == pygame.MOUSEMOTION:
                # mouse movement event
                if pygame.mouse.get_pressed()[0]:
                    # left click, move camera
                    if self.mouse_mvt is not None:
                        self.mouse_mvt = pygame.mouse.get_rel()
                        self.camera.center[0] -= (float(self.mouse_mvt[0]) / self.window_size[0])
                        self.camera.center[1] -= (float(self.mouse_mvt[1]) / self.window_size[1])
                    else:
                        self.mouse_mvt = pygame.mouse.get_rel()
                elif pygame.mouse.get_pressed()[2]:
                    # right click, rotate camera
                    if self.mouse_mvt is not None:
                        self.mouse_mvt = pygame.mouse.get_rel()
                        self.camera.phi -= (float(self.mouse_mvt[0]) / self.window_size[0])
                        self.camera.psi -= (float(self.mouse_mvt[1]) / self.window_size[1])
                    else:
                        self.mouse_mvt = pygame.mouse.get_rel()
                else:
                    self.mouse_mvt = None

    def run(self):
        """
        Draw the scene until exit
        """
        self.running = True
        while self.running:
            self.pygameEvents()
            self.draw()
