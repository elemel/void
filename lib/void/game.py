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

import sys, random, math, pyglet
from pyglet.gl import *
from void.asteroid import Asteroid
import void.box2d as box2d
from void.hub import Hub
from void.ship import Ship

class Game(object):
    def __init__(self):
        self.world = self.create_world()
        self.contact_results = []
        self.contact_listener = VoidContactListener(self)
        self.world.SetContactListener(self.contact_listener)
        self.hub = Hub(self.world)
        self.ship = Ship(self.world)

    def step(self, dt):
        maybe_dead = set()
        if random.random() <= dt:
            Asteroid(self.world, self.ship)
        self.ship.step(dt)
        self.step_laser(dt, maybe_dead)
        self.world.Step(dt, 10, 8)
        for agent_1, agent_2 in self.contact_results:
            maybe_dead.add(agent_1)
            maybe_dead.add(agent_2)
            agent_1.collide(agent_2)
            agent_2.collide(agent_1)
        for agent in maybe_dead:
            if not agent.alive:
                if type(agent) is Asteroid:
                    agent.split()
                self.world.DestroyBody(agent.body)
        del self.contact_results[:]

    def step_laser(self, dt, maybe_dead):
        if self.ship.firing:
            angle = self.ship.body.GetAngle()
            unit = box2d.b2Vec2(-math.sin(angle), math.cos(angle))
            segment = box2d.b2Segment()
            segment.p1 = self.ship.body.GetPosition()
            segment.p2 = segment.p1 + unit * 10.0
            fraction, normal, shape = self.world.RaycastOne(segment, False,
                                                            None)
            if shape is not None:
                agent = shape.GetBody().GetUserData()
                if type(agent) is Asteroid:
                    maybe_dead.add(agent)
                    agent.power -= dt * fraction
        
    def on_draw(self):
        glScaled(15.0, 15.0, 15.0)
        position = self.ship.body.GetPosition()
        glTranslated(-position.x, -position.y, 0.0)
        self.draw_lifeline()
        self.draw_towline()
        self.draw_laser()
        for agent in self.query_draw():
            agent.draw()

    def query_draw(self):
        position = self.ship.body.GetPosition()
        aabb = box2d.b2AABB()
        aabb.lowerBound.Set(position.x - 40.0, position.y - 25.0)
        aabb.upperBound.Set(position.x + 40.0, position.y + 25.0)
        max_count = 100
        (count, shapes) = self.world.Query(aabb, max_count)
        agents = set(shape.GetBody().GetUserData() for shape in shapes)
        agents = sorted(agents, key=id)
        return agents
    
    def draw_lifeline(self):
        position = self.ship.body.GetPosition()
        distance = math.sqrt(position.x ** 2 + position.y ** 2)
        fraction = distance / self.ship.max_lifeline_range
        if fraction <= 0.5:
            red = fraction * 2.0
            green = 1.0
        else:
            red = 1.0
            green = 1.0 - (fraction - 0.5) * 2.0
        glBegin(GL_LINES)
        glColor4d(red, green, 0.0, 1.0)
        glVertex2d(0.0, 0.0)
        glVertex2d(position.x, position.y)
        glEnd()

    def draw_towline(self):
        joint_edge = self.ship.body.GetJointList()
        if joint_edge is not None:
            joint = joint_edge.joint
            anchor_1 = joint.GetAnchor1()
            anchor_2 = joint.GetAnchor2()
            glBegin(GL_LINES)
            glColor3d(1.0, 0.0, 1.0)
            glVertex2d(anchor_1.x, anchor_1.y)
            glVertex2d(anchor_2.x, anchor_2.y)
            glEnd()

    def draw_laser(self):
        if self.ship.firing:
            position = self.ship.body.GetPosition()
            angle = self.ship.body.GetAngle()
            unit = box2d.b2Vec2(-math.sin(angle), math.cos(angle))
            endpoint = position + unit * 10.0
            glBegin(GL_LINES)
            glColor4d(1.0, 0.0, 0.0, 1.0)
            glVertex2d(position.x, position.y)
            glColor4d(1.0, 0.0, 0.0, 0.0)
            glVertex2d(endpoint.x, endpoint.y)
            glEnd()

    def create_world(self):
        world_aabb = box2d.b2AABB()
        world_aabb.lowerBound.Set(-400.0, -400.0)
        world_aabb.upperBound.Set(400.0, 400.0)
        gravity = box2d.b2Vec2(0.0, 0.0)
        return box2d.b2World(world_aabb, gravity, False)

    def contact_result(self, point):
        agent_1 = point.shape1.GetBody().GetUserData()
        agent_2 = point.shape2.GetBody().GetUserData()
        self.contact_results.append((agent_1, agent_2))

class VoidContactListener(box2d.b2ContactListener):
    def __init__(self, window):
        super(VoidContactListener, self).__init__() 
        self.window = window

    def Add(self, point):
        pass

    def Persist(self, point):
        pass

    def Remove(self, point):
        pass

    def Result(self, point):
        self.window.contact_result(point)
