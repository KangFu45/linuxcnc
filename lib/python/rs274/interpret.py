#    This is a component of AXIS, a front-end for emc
#    Copyright 2004, 2005, 2006 Jeff Epler <jepler@unpythonic.net>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
import math, gcode

class RotVector:
    def __init__(self,_x,_y,_z):
        self.x = _x
        self.y = _y
        self.z = _z

    def normalize(self):
        return math.sqrt(self.x*self.x+self.y*self.y+self.z*self.z)

class RotMatrix3:
    def __init__(self,_a1,_a2,_a3
                 ,_b1,_b2,_b3
                 ,_c1,_c2,_c3):
        self.a1 = _a1
        self.a2 = _a2
        self.a3 = _a3
        self.b1 = _b1
        self.b2 = _b2
        self.b3 = _b3
        self.c1 = _c1
        self.c2 = _c2
        self.c3 = _c3

    def init_unit(self):
        return RotMatrix3(1.,0.,0.
                          ,0.,1.,0.
                          ,0.,0.,1.)

class RotMatrix4:
    def __init__(self,mat3):
        self.a1 = mat3.a1
        self.a2 = mat3.a2
        self.a3 = mat3.a3
        self.a4 = 0.
        self.b1 = mat3.b1
        self.b2 = mat3.b2
        self.b3 = mat3.b3
        self.b4 = 0.
        self.c1 = mat3.c1
        self.c2 = mat3.c2
        self.c3 = mat3.c3
        self.c4 = 0.
        self.d1 = 0.
        self.d2 = 0.
        self.d3 = 0.
        self.d4 = 1.

    def list(self):
        return [self.a1,self.a2,self.a3,self.a4
                ,self.b1,self.b2,self.b3,self.b4
                ,self.c1,self.c2,self.c3,self.c4
                ,self.d1,self.d2,self.d3,self.d4]

class RotMath:
    def dot(self,vec1,vec2):
        return vec1.x*vec2.x + vec1.y*vec2.y + vec1.z*vec2.z

    def cross(self,vec1,vec2):
        return RotVector(vec1.y*vec2.z - vec1.z*vec2.y
                         ,vec1.z*vec2.x - vec1.x*vec2.z
                         ,vec1.x*vec2.y - vec1.y*vec2.x)

    def nor_rot_mat3(self,vec1,vec2):
        angle = math.acos(self.dot(vec1,vec2) / vec1.normalize() / vec2.normalize())
        axis = self.cross(vec1,vec2)

        norm = axis.normalize()
        axis.x = axis.x / norm
        axis.y = axis.y / norm
        axis.z = axis.z / norm

        return RotMatrix3(math.cos(angle) + axis.x * axis.x * (1 - math.cos(angle))
                          ,axis.x * axis.y * (1 - math.cos(angle) - axis.z * math.sin(angle))
                          ,axis.y * math.sin(angle) + axis.x * axis.z * (1 - math.cos(angle))
                          ,axis.z * math.sin(angle) + axis.x * axis.y * (1 - math.cos(angle))
                          ,math.cos(angle) + axis.y * axis.y * (1 - math.cos(angle))
                          ,-axis.x * math.sin(angle) + axis.y * axis.z * (1 - math.cos(angle))
                          ,-axis.y * math.sin(angle) + axis.x * axis.z * (1 - math.cos(angle))
                          ,axis.x * math.sin(angle) + axis.y * axis.z * (1 - math.cos(angle))
                          ,math.cos(angle) + axis.z * axis.z * (1 - math.cos(angle)))

    def nor_rot_mat3_xy(self,vec2):
        vec1 = RotVector(0,0,1)
        return self.nor_rot_mat3(vec1,vec2)

    def nor_un_rot_mat3_xy(self,vec1):
        vec2 = RotVector(0,0,1)
        return self.nor_rot_mat3(vec1,vec2)

    def nor_rot_mat3_xy_exe(self,vec2,x,y,z):
        mat3 = self.nor_rot_mat3_xy(vec2)
        t1 = mat3.a1 * x + mat3.a2 * y + mat3.a3 * z
        t2 = mat3.b1 * x + mat3.b2 * y + mat3.b3 * z
        z = mat3.c1 * x + mat3.c2 * y + mat3.c3 * z
        x = t1
        y = t2
        return [x,y,z]

    def nor_un_rot_mat3_xy_exe(self,vec1,x,y,z):
        mat3 = self.nor_un_rot_mat3_xy(vec1)
        t1 = mat3.a1 * x + mat3.a2 * y + mat3.a3 * z
        t2 = mat3.b1 * x + mat3.b2 * y + mat3.b3 * z
        z = mat3.c1 * x + mat3.c2 * y + mat3.c3 * z
        x = t1
        y = t2
        return [x,y,z]

class Translated:
    g92_offset_x = g92_offset_y = g92_offset_z = 0
    g92_offset_a = g92_offset_b = g92_offset_c = 0
    g92_offset_u = g92_offset_v = g92_offset_w = 0
    g5x_offset_x = g5x_offset_y = g5x_offset_z = 0
    g5x_offset_a = g5x_offset_b = g5x_offset_c = 0
    g5x_offset_u = g5x_offset_v = g5x_offset_w = 0
    x_rotation_normal = y_rotation_normal = z_rotation_normal = 1
    rotation_xy = 0

    def rotate_and_translate(self, x,y,z,a,b,c,u,v,w):
        x += self.g92_offset_x
        y += self.g92_offset_y
        z += self.g92_offset_z
        a += self.g92_offset_a
        b += self.g92_offset_b
        c += self.g92_offset_c
        u += self.g92_offset_u
        v += self.g92_offset_v
        w += self.g92_offset_w

        if self.x_rotation_normal or self.y_rotation_normal or self.z_rotation_normal:
            vec2 = RotVector(self.x_rotation_normal
                             ,self.y_rotation_normal
                             ,self.z_rotation_normal)
            xyz = RotMath.nor_rot_mat3_xy_exe(vec2,x,y,z)
            x = xyz[0]
            y = xyz[1]
            z = xyz[2]

        #if self.rotation_xy:
        #    rotx = x * self.rotation_cos - y * self.rotation_sin
        #    y = x * self.rotation_sin + y * self.rotation_cos
        #    x = rotx

        x += self.g5x_offset_x
        y += self.g5x_offset_y
        z += self.g5x_offset_z
        a += self.g5x_offset_a
        b += self.g5x_offset_b
        c += self.g5x_offset_c
        u += self.g5x_offset_u
        v += self.g5x_offset_v
        w += self.g5x_offset_w

        return [x, y, z, a, b, c, u, v, w]

    def straight_traverse(self, *args):
        self.straight_traverse_translated(*self.rotate_and_translate(*args))
    def straight_feed(self, *args):
        self.straight_feed_translated(*self.rotate_and_translate(*args))
    def set_g5x_offset(self, index, x, y, z, a, b, c, u=None, v=None, w=None):
        self.g5x_index = index
        self.g5x_offset_x = x
        self.g5x_offset_y = y
        self.g5x_offset_z = z
        self.g5x_offset_a = a
        self.g5x_offset_b = b
        self.g5x_offset_c = c
        self.g5x_offset_u = u
        self.g5x_offset_v = v
        self.g5x_offset_w = w
    def set_g92_offset(self, x, y, z, a, b, c, u=None, v=None, w=None):
        self.g92_offset_x = x
        self.g92_offset_y = y
        self.g92_offset_z = z
        self.g92_offset_a = a
        self.g92_offset_b = b
        self.g92_offset_c = c
        self.g92_offset_u = u
        self.g92_offset_v = v
        self.g92_offset_w = w
    def set_xy_rotation(self, theta):
        self.rotation_xy = theta
        t = math.radians(theta)
        self.rotation_sin = math.sin(t)
        self.rotation_cos = math.cos(t)
    def set_xyz_rotation_normal(self,x,y,z):
        self.x_rotation_normal = x
        self.y_rotation_normal = y
        self.z_rotation_normal = z

class ArcsToSegmentsMixin:
    plane = 1
    arcdivision = 64

    def set_plane(self, plane):
        self.plane = plane

    def arc_feed(self, x1, y1, cx, cy, rot, z1, a, b, c, u, v, w):
        self.lo = tuple(self.lo)
        segs = gcode.arc_to_segments(self, x1, y1, cx, cy, rot, z1, a, b, c, u, v, w, self.arcdivision)
        self.straight_arcsegments(segs)

class PrintCanon:
    def set_g5x_offset(self, *args):
        print("set_g5x_offset", args)

    def set_g92_offset(self, *args):
        print("set_g92_offset", args)

    def next_line(self, state):
        print("next_line", state.sequence_number)
        self.state = state

    def set_plane(self, plane):
        print("set plane", plane)

    def set_feed_rate(self, arg):
        print("set feed rate", arg)

    def comment(self, arg):
        print("#", arg)

    def straight_traverse(self, *args):
        print("straight_traverse %.4g %.4g %.4g  %.4g %.4g %.4g" % args)

    def straight_feed(self, *args):
        print("straight_feed %.4g %.4g %.4g  %.4g %.4g %.4g" % args)

    def dwell(self, arg):
        if arg < .1:
            print("dwell %f ms" % (1000 * arg))
        else:
            print("dwell %f seconds" % arg)

    def arc_feed(self, *args):
        print("arc_feed %.4g %.4g  %.4g %.4g %.4g  %.4g  %.4g %.4g %.4g" % args)

class StatMixin:
    def __init__(self, s, r):
        self.s = s
        self.tools = list(s.tool_table)
        self.random = r

    def change_tool(self, pocket):
        if self.random:
            self.tools[0], self.tools[pocket] = self.tools[pocket], self.tools[0]
        elif pocket==0:
            self.tools[0] = -1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0
        else:
            self.tools[0] = self.tools[pocket]

    def get_tool(self, pocket):
        if pocket >= 0 and pocket < len(self.tools):
            return tuple(self.tools[pocket])
        return -1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0

    def get_external_angular_units(self):
        return self.s.angular_units or 1.0

    def get_external_length_units(self):
        return self.s.linear_units or 1.0

    def get_axis_mask(self):
        return self.s.axis_mask

    def get_block_delete(self):
        return self.s.block_delete


# vim:ts=8:sts=4:et:
