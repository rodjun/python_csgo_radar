import os
from ctypes import sizeof
from csgo.game_structures import dheader_t, dplane_t, dnode_t, dleaf_t


# pep-8 hell ahead
class BspTrace:
    def __init__(self, csgo_folder):
        self.csgo_folder = csgo_folder
        self.header = dheader_t()
        self.map_path = ""

    def change_map(self, map_path):
        self.handle = open(os.path.join(self.csgo_folder, map_path), "rb")
        self.map_path = map_path
        self.handle.readinto(self.header)
        self.planeLump = self.getLumpFromId(1)
        self.nodeLump = self.getLumpFromId(5)
        self.leafLump = self.getLumpFromId(10)
        print("Map changed to {}".format(self.map_path))

    def getLumpFromId(self, id):
        lump = []
        if id == 1:
            numLumps = self.header.lumps[id].filelen // sizeof(dplane_t)
            for i in range(numLumps):
                lump.append(dplane_t())
        elif id == 5:
            numLumps = self.header.lumps[id].filelen // sizeof(dnode_t)
            for i in range(numLumps):
                lump.append(dnode_t())
        elif id == 10:
            numLumps = self.header.lumps[id].filelen // sizeof(dleaf_t)
            for i in range(numLumps):
                lump.append(dleaf_t())

        for i in range(numLumps):
            self.handle.seek(self.header.lumps[id].fileofs + (i * sizeof(lump[i])))
            self.handle.readinto(lump[i])

        return lump

    def getLeafFromPoint(self, point):
        node = 0

        pNode = None
        pPlane = None

        d = 0

        while node >= 0:
            pNode = self.nodeLump[node]
            pPlane = self.planeLump[pNode.planenum]

            d = point.dot_product(pPlane.normal) - pPlane.dist  # d = D3DXVec3Dot(&point, &pPlane->normal) - pPlane->dist;

            if d > 0:
                node = pNode.children[0]
            else:
                node = pNode.children[1]

        return self.leafLump[-node - 1]

    def isVisible(self, vStart, vEnd):
        vDirection = vEnd - vStart
        vPoint = vStart

        iStepCount = int(vDirection.length())

        vDirection /= iStepCount

        pLeaf = None

        while (iStepCount):
            vPoint = vPoint + vDirection

            pLeaf = self.getLeafFromPoint(vPoint)

            if pLeaf and (pLeaf.contents & 0x1):
                break

            iStepCount -= 1
        if pLeaf is None:
            return False
        else:
            return not (pLeaf.contents & 0x1)
