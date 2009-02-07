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
from void.asteroid import Asteroid
from void.shot import Shot

class Ship(Agent):
    def __init__(self, world):
        self.world = world
        self.color = (1.0, 1.0, 1.0)
        self.thrust = False
        self.firing = False
        self.turn = 0.0
        self.max_cooldown = 0.3
        self.cooldown = 0.0
        self.max_angular_velocity = 2.0 * math.pi
        self.body = self.create_body(world)

    def create_body(self, world):
        body_def = box2d.b2BodyDef()
        body_def.position.Set(0.0, 0.0)
        body_def.angle = 2.0 * math.pi * random.random()

        shape_def = box2d.b2PolygonDef()
        shape_def.setVertices_tuple([(-1.0, -1.0), (1.0, -1.0), (0.0, 2.0)])
        shape_def.density = 2.0
        shape_def.restitution = 1.0
        shape_def.filter.categoryBits = 0x0001
        shape_def.filter.maskBits = 0x0002

        body = world.CreateBody(body_def)
        body.CreateShape(shape_def)
        body.SetMassFromShapes()
        body.SetUserData(self)
        return body

    def step(self, dt):
        angle = self.body.GetAngle()
        force = self.thrust * 200.0 * box2d.b2Vec2(-math.sin(angle),
                                                   math.cos(angle))
        point = self.body.GetPosition()
        self.body.ApplyForce(force, point)
        self.cooldown -= dt
        if self.firing and self.cooldown <= 0.0:
            Shot(self.world, self)
            self.cooldown = self.max_cooldown
        self.body.SetAngularVelocity(self.turn *
                                     self.max_angular_velocity)

    def toggle_towline(self):
        joint_edge = self.body.GetJointList()
        if joint_edge is not None:
            self.world.DestroyJoint(joint_edge.joint)
            return

        position = self.body.GetPosition()
        aabb = box2d.b2AABB()
        aabb.lowerBound.Set(position.x - 10.0, position.y - 10.0)
        aabb.upperBound.Set(position.x + 10.0, position.y + 10.0)
        max_count = 100
        (count, shapes) = self.world.Query(aabb, max_count)
        agents = set(shape.GetBody().GetUserData() for shape in shapes)
        asteroids = list(agent for agent in agents if type(agent) is Asteroid)
        if asteroids:
            asteroid = random.choice(asteroids)
            joint_def = box2d.b2DistanceJointDef()
            joint_def.Initialize(self.body, asteroid.body,
                                 self.body.GetPosition(),
                                 asteroid.body.GetPosition())
            joint_def.collideConnected = True
            self.world.CreateJoint(joint_def)
