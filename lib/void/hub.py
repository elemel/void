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

from void.agent import Agent
import void.box2d as box2d

class Hub(Agent):
    def __init__(self, world):
        self.world = world
        self.color = (0.5, 0.5, 0.0)
        self.body = self.create_body(world)

    def create_body(self, world):
        body_def = box2d.b2BodyDef()
        body_def.position.Set(0.0, 0.0)

        shape_def = box2d.b2PolygonDef()
        shape_def.setVertices_tuple([(-3.0, -3.0), (3.0, -3.0), (3.0, 3.0),
                                     (-3.0, 3.0)])
        shape_def.restitution = 1.0
        shape_def.filter.categoryBits = 0x0001
        shape_def.filter.maskBits = 0x0002

        body = world.CreateBody(body_def)
        body.CreateShape(shape_def)
        body.SetMassFromShapes()
        body.SetUserData(self)
        return body