class Material:
    """
    Material class that holds material data
    """
    def __init__(self, name=None, Ka=[0., 0., 0.], Kd=[0.4, 0.3, 0.25], Ks=[0.5, 0.4, 0.35], Ns=10.0):
        """
        Initialise material
        :param name: material name
        :param Ka: ambient reflectivity
        :param Kd: diffuse reflectivity
        :param Ks: specular reflectivity
        :param Ns: specular exponent
        """
        self.name = name
        self.Ka = Ka
        self.Kd = Kd
        self.Ks = Ks
        self.Ns = Ns


class MaterialLibrary:
    """
    Material library class that holds materials
    """
    def __init__(self):
        """
        Initialise library
        """
        self.materials = []
        self.names = {}

    def add_material(self, material):
        """
        Add a material to material library
        :param material: material to add
        """
        self.names[material.name] = len(self.materials)
        self.materials.append(material)
