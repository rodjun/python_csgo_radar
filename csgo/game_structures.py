import math
from ctypes import Structure, c_float, c_int, c_char, c_short, c_ushort, c_byte


class Vector3(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float),
                ("z", c_float)]

    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def dot_product(self, dot):
        return self.x * dot.x + self.y * dot.y + self.z * dot.z

    def distance_from(self, other):
        return math.sqrt(((self.x - other.x) ** 2) + ((self.y - other.y) ** 2) + ((self.z - other.z) ** 2))

    def normalize(self):
        size = self.length()
        if size != 0:
            self.x /= size
            self.y /= size
            self.z /= size

    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        self.z += other.z

        return self

    def __truediv__(self, other):
        if isinstance(other, Vector3):  # Vector division
            self.x /= other.x
            self.y /= other.y
            self.z /= other.z
        elif isinstance(other, int):  # Divide by a sigle number
            if other != 0:
                self.x /= other
                self.y /= other
                self.z /= other
        return self


class Vector2(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float)]

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def dot_product(self, dot):
        return self.x * dot.x + self.y * dot.y

    def distance_from(self, other):
        return math.sqrt(((self.x - other.x) ** 2) + ((self.y - other.y) ** 2))

    def normalize(self):
        size = self.length()
        if size != 0:
            self.x /= size
            self.y /= size

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y

        return self

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y

        return self

    def __idiv__(self, other):
        if type(other) is Vector3:  # Vector division
            self.x /= other.x
            self.y /= other.y
        else:  # Divide by a sigle number
            self.x /= other
            self.y /= other
        return self

    def __imul__(self, other):
        if type(other) is Vector3:  # Vector division
            self.x *= other.x
            self.y *= other.y
        else:  # Divide by a sigle number
            self.x *= other
            self.y *= other
        return self

    @classmethod
    def from_vec3(cls, vec):
        return cls(vec.x, vec.y)


class Entity(object):
    def __init__(self):
        self.health = c_int()
        self.team = c_int()
        self.origin = Vector3()
        self.angles = Vector3()
        self.is_valid = False

    def update_info(self, process, base_ptr, netvars, valid):
        if valid:
            process.read_memory(base_ptr + netvars['m_iHealth'], self.health)
            process.read_memory(base_ptr + netvars['m_iTeamNum'], self.team)
            process.read_memory(base_ptr + netvars['m_vecOrigin'], self.origin)
            self.is_valid = self.health.value > 0
        else:
            self.is_valid = False


class lump_t(Structure):
    _fields_ = [("fileofs", c_int),
                ("filelen", c_int),
                ("version", c_int),
                ("fourCC", c_char * 4)]


class dheader_t(Structure):
    _fields_ = [("ident", c_int),
                ("version", c_int),
                ("lumps", lump_t * 64),
                ("mapRevision", c_int)]


class dplane_t(Structure):
    _fields_ = [("normal", Vector3),
                ("dist", c_float),
                ("type", c_int)]


class dnode_t(Structure):
    _fields_ = [("planenum", c_int),
                ("children", c_int * 2),
                ("mins", c_short * 3),
                ("maxs", c_short * 3),
                ("firsface", c_ushort),
                ("numfaces", c_ushort),
                ("area", c_short)]


class dleaf_t(Structure):
    _fields_ = [("contents", c_int),
                ("cluster", c_short),
                ("pad_bitfields", c_byte * 2),  # it's a pain in the ass to add bit fields with CTYPES, the two bit fields used on this struct add to a total of 16 bits so we just use 2 bytes
                ("mins", c_short * 3),
                ("maxs", c_short * 3),
                ("firstleafface", c_ushort),
                ("numleaffaces", c_ushort),
                ("firstleafbrush", c_ushort),
                ("numleafbrushes", c_ushort),
                ("leafWaterDataID", c_short)]