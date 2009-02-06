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

import math, random
from void.agent import Agent
import void.box2d as box2d

class Asteroid(Agent):
    def __init__(self, world, radius=None, position=None,
                 linear_velocity=None):
        self.world = world
        if radius is None:
            radius = 3.0 * (1.0 + random.random())
        if position is None:
            angle = 2.0 * math.pi * random.random()
            unit = box2d.b2Vec2(-math.sin(angle), math.cos(angle))
            distance = 15.0 * (1.0 + random.random())
            position = unit * distance
        if linear_velocity is None:
            angle = 2.0 * math.pi * random.random()
            unit = box2d.b2Vec2(-math.sin(angle), math.cos(angle))
            linear_velocity = unit * 4.0 * (1.0 + random.random())
        self.radius = radius
        self.color = (0.5 * random.random(), 0.5 * random.random(),
                      0.5 * random.random() + 0.5)
        self.body = self.create_body(position, linear_velocity)

    def create_body(self, position, linear_velocity):
        body_def = box2d.b2BodyDef()
        body_def.position = position
        body_def.angle = 2.0 * math.pi * random.random()

        shape_def = box2d.b2PolygonDef()
        vertices = []
        for i in xrange(5):
            angle = (i + random.random()) / 5.0 * 2.0 * math.pi
            x = self.radius * math.cos(angle)
            y = self.radius * math.sin(angle)
            vertices.append((x, y))
        shape_def.setVertices_tuple(vertices)
        shape_def.density = 1.0
        shape_def.restitution = 1.0
        shape_def.filter.categoryBits = 0x0002
        shape_def.filter.maskBits = 0x0001

        body = self.world.CreateBody(body_def)
        body.CreateShape(shape_def)
        body.SetMassFromShapes()
        body.SetLinearVelocity(linear_velocity)
        body.SetAngularVelocity(random.random() - 0.5)
        body.SetUserData(self)
        return body

    def split(self):
        if self.radius < 2.0:
            return []
        fraction = (1.0 + random.random()) / 3.0
        radius_1 = self.radius * math.sqrt(fraction)
        radius_2 = math.sqrt(self.radius ** 2 - radius_1 ** 2)
        position = self.body.GetPosition()
        angle = random.random() * 2.0 * math.pi
        unit = box2d.b2Vec2(-math.sin(angle), math.cos(angle))
        position_1 = position + unit * radius_2
        position_2 = position - unit * radius_1
        linear_velocity = self.body.GetLinearVelocity()
        agent_1 = Asteroid(self.world, radius_1, position_1, linear_velocity)
        agent_2 = Asteroid(self.world, radius_2, position_2, linear_velocity)
        return agent_1, agent_2
