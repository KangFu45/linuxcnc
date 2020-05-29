import os
import sys

o_path = os.getcwd()
sys.path.append(o_path)
from rs274 import  interpret

x = y = z = 10

rot_math = interpret.RotMath()
xyz = rot_math.nor_un_rot_mat3_xy_exe(interpret.RotVector(1,1,1), x, y, z)
print (xyz[0],xyz[1],xyz[2])
