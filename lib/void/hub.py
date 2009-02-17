# Copyright (c) 2008 Mikael Lind
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

import math
from pyglet.gl import *
from void.agent import Agent
from void.asteroid import Asteroid
import void.box2d as box2d

class Hub(Agent):
    def __init__(self, world):
        super(Hub, self).__init__(world)
        self.color = (1.0, 1.0, 1.0)
        self.radius = 5.0
        self.vertices = []
        vertex_count = 90
        for i in xrange(vertex_count):
            angle = i * 2.0 * math.pi / vertex_count
            vertex = self.radius * box2d.b2Vec2(-math.sin(angle),
                                                math.cos(angle))
            self.vertices.append(vertex)
        self.body = self.create_body(world)

    def create_body(self, world):
        body_def = box2d.b2BodyDef()
        body_def.position.Set(0.0, 0.0)

        shape_def = box2d.b2CircleDef()
        shape_def.radius = self.radius
        # shape_def.restitution = 1.0
        shape_def.filter.categoryBits = 0x0001
        shape_def.filter.maskBits = 0x0002
        shape_def.isSensor = True

        body = world.CreateBody(body_def)
        body.CreateShape(shape_def)
        body.SetMassFromShapes()
        body.SetUserData(self)
        return body

    def draw_geometry(self):
        glBegin(GL_LINE_LOOP)
        glColor3d(*self.color)
        for vertex in self.vertices:
            glVertex2d(vertex.x, vertex.y)
        glEnd()

    def collide(self, other):
        if type(other) is Asteroid:
            other.alive = False
