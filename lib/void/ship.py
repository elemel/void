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

import math, random, sys
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
        self.max_cooldown = 0.2
        self.cooldown = 0.0
        self.max_angular_velocity = 2.0 * math.pi
        self.max_towing_range = 10.0
        self.max_towing_capacity = 20.0
        self.max_lifeline_range = 200.0
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
        position = self.body.GetPosition()
        distance = math.sqrt(position.x ** 2 + position.y ** 2)
        if distance > self.max_lifeline_range:
            print "Game Over: Out of Range"
            sys.exit()
        angle = self.body.GetAngle()
        force = self.thrust * 200.0 * box2d.b2Vec2(-math.sin(angle),
                                                   math.cos(angle))
        self.body.ApplyForce(force, position)
        self.cooldown -= dt
        if self.firing and self.cooldown <= 0.0:
            Shot(self.world, self)
            self.cooldown = self.max_cooldown
        self.body.SetAngularVelocity(self.turn * self.max_angular_velocity)

    def toggle_towline(self):
        joint_edge = self.body.GetJointList()
        if joint_edge is not None:
            self.world.DestroyJoint(joint_edge.joint)
            return

        position = self.body.GetPosition()
        aabb = box2d.b2AABB()
        aabb.lowerBound.Set(position.x - self.max_towing_range,
                            position.y - self.max_towing_range)
        aabb.upperBound.Set(position.x + self.max_towing_range,
                            position.y + self.max_towing_range)
        max_count = 100
        (count, shapes) = self.world.Query(aabb, max_count)
        targets = set(shape.GetBody().GetUserData() for shape in shapes)
        targets = list(target for target in targets if self.can_tow(target))
        if targets:
            target = random.choice(targets)
            joint_def = box2d.b2DistanceJointDef()
            joint_def.Initialize(self.body, target.body,
                                 self.body.GetPosition(),
                                 target.body.GetPosition())
            joint_def.collideConnected = True
            self.world.CreateJoint(joint_def)

    def can_tow(self, other):
        if type(other) is not Asteroid:
            return False
        if other.body.GetMass() > self.max_towing_capacity:
            return False
        offset = self.body.GetPosition() - other.body.GetPosition()
        distance = math.sqrt(offset.x ** 2 + offset.y ** 2)
        return distance <= self.max_towing_range
