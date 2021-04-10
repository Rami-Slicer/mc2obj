from minecraft_model_reader.api import Block
from minecraft_model_reader.api.resource_pack.java import (
    JavaResourcePack,
    JavaResourcePackManager,
)
import io
import re

class Vector3f:
    x: float
    y: float
    z: float

    def __init__(self, x: float, y: float, z: float):
        # if(not x is float):
        #     raise Exception(x)
        #     pass
        # if(not y is float):
        #     raise Exception(y)
        #     pass
        # if(not z is float):
        #     raise Exception(z)
        #     pass
        self.x = x
        self.y = y
        self.z = z
        pass
    pass

class Vertex:

    pos: Vector3f
    texcoords = []

    def __init__(self, pos: Vector3f, texcoords: list):
        self.pos = pos
        self.texcoords = texcoords
        pass
    pass

class Triangle:
    indices = []
    texcoord_indices = []

    def __init__(self, indices: list, texcoord_indices: list):
        self.indices = indices
        self.texcoord_indices = texcoord_indices
        pass
    pass


class Mesh:
    vertices = []
    indices = []

    def __init__(self, vertices: list, indices: list):
        self.vertices = vertices
        self.indices = indices
        pass
    pass

re_texturename = re.compile(r"/(\w+)\.png")

class OBJWriter:
    from typing import Tuple
    fstr_vertex = "v {} {} {}\n"
    fstr_texcoord = "vt {} {}\n"
    fstr_face = "f {}/{} {}/{} {}/{}\n"
    fstr_mat = "usemtl {}\n"

    

    stream: str
    textures: Tuple[str, ...]

    def __init__(self, stream: io.StringIO, textures: tuple):
        self.stream = stream
        # self.stream.write(self.fstr_mat.format("stone"))
        
        self.textures = textures
        pass

    def write_vert(self, write: Vertex):
        # print(self.fstr_vertex.format(write.pos.x, write.pos.y, write.pos.z))
        self.stream.write(
            self.fstr_vertex.format(write.pos.x, write.pos.y, write.pos.z)
        )
        self.stream.write(
            self.fstr_texcoord.format(write.texcoords[0], write.texcoords[1])
        )
        pass

    def write_face(self, indices: list, texindices: int):
        # print(self.textures[texindices])
        path = re.search(re_texturename, self.textures[texindices])
        
        self.stream.write(self.fstr_mat.format(path.group(1)))
        self.stream.write(
            self.fstr_face.format(
                indices[0]+1, 
                indices[0]+1, 
                indices[1]+1, 
                indices[1]+1, 
                indices[2]+1, 
                indices[2]+1
            )
        )
        pass
    pass


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]



def convert(pack_path: str, blockstate: str, output_path=""):
    """Convert a Minecraft JSON model in a resource pack to a obj/mtl file pair. Data values like minecraft:water[level=2] are supported."""

    pack = JavaResourcePack(pack_path)
    resource_pack = JavaResourcePackManager([pack])
    block: Block = Block.from_string_blockstate(blockstate)
    block_model = resource_pack.get_block_model(block)
    block_model.vert_tables


    



    # def chunks(l, n):
    #     n = max(1, n)
    #     return (l[i:i+n] for i in range(0, len(l), n))

    # print(block_model.face_mode)
    # print(block_model.verts)
    # print(block_model.faces)
    # print(block_model.texture_coords)
    verts_dict = block_model.verts
    indices_dict = block_model.faces
    texindices_dict = block_model.texture_index
    texcoords_dict = block_model.texture_coords




    verts_arr = []
    indices_arr = []
    texindices_arr = []
    texcoords_arr = []

    order = [
        "up",
        "down",
        "north",
        "south",
        "east",
        "west",
        None
    ]

    vert_offsets = []

    # 
    for dir in order:
        print(dir)
        # dir = "west"
        if dir in verts_dict.keys(): verts_arr.extend(verts_dict[dir].tolist())
        if dir in indices_dict.keys(): indices_arr.append((indices_dict[dir]))
        if dir in texindices_dict.keys(): texindices_arr.extend((texindices_dict[dir]))
        if dir in texcoords_dict.keys(): texcoords_arr.extend((texcoords_dict[dir]))

    indice_buf = []
    maximum = 0
    # print(indices_arr)
    for i in range(len(indices_arr)):
        # print(indices_arr[i])

        for j in range(len(indices_arr[i])):
            indice = indices_arr[i][j]
            if i > 0:
                indice += maximum
                # print(indice)

            indice_buf.append(indice)
            pass
        pass
        maximum += max(indices_arr[i]+1)
        # indice_buf.extend(indices_arr[i])

    indices_arr = indice_buf

    # print(indices_dict)

    texcoord_chunks = list(chunks(texcoords_arr, 2))
    verts_chunks = list(chunks(verts_arr, 3))
    indices_chunks = list(chunks(indices_arr, 3))

    # print(indices_dict)


    # print(verts_arr)
    # print(indices_arr)





    with open("{}{}.obj".format(output_path, blockstate), 'w') as obj_file:
        writer = OBJWriter(obj_file, block_model.textures)
        
        for i in range(len(verts_chunks)):
            pos = Vector3f(verts_chunks[i][0], verts_chunks[i][1], verts_chunks[i][2])
            vert = Vertex(pos, texcoord_chunks[i])
            writer.write_vert(vert)
            pass
        
        for i in range(len(indices_chunks)):
            # print(i)
            writer.write_face(indices_chunks[i], texindices_arr[i])
            pass

        obj_file.write("mtllib {}.mtl".format(blockstate))
        pass

    fstr_mtl = '''
    newmtl {}
    Ka 1.000 1.000 1.000
    Kd 1.000 1.000 1.000
    Ks 0.000 0.000 0.000

    d 1.0
    illum 2
    map_Kd {}
    '''

    mtl_file = open("{}{}.mtl".format(output_path, blockstate), 'w')
    for i in block_model.textures:
        path = re.search(re_texturename, i)
        mtl_file.write(
            fstr_mtl.format(
                path.group(1),
                i
            )
        )

