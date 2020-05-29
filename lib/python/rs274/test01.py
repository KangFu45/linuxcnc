from interpret import *

#vec2 = RotVector(1,1,1)
mmm = RotMath()
mat3 = mmm.nor_rot_mat3_xy(RotVector(1,1,1))
print (mat3.b1,mat3.b2,mat3.b3)
