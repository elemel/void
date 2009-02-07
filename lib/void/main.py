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

import sys, random, math, numpy, pyglet
from pyglet.gl import *
from void.asteroid import Asteroid
import void.box2d as box2d
from void.hub import Hub
from void.ship import Ship
from void.shot import Shot

class VoidWindow(pyglet.window.Window):
    def __init__(self):
        pyglet.window.Window.__init__(self, fullscreen=True, caption="Void")
        self.set_mouse_visible(False)
        self.world = self.create_world()
        self.contact_results = []
        self.contact_listener = VoidContactListener(self)
        self.world.SetContactListener(self.contact_listener)
        self.hub = Hub(self.world)
        self.ship = Ship(self.world)
        for _ in xrange(20):
            Asteroid(self.world)
        pyglet.clock.schedule_interval(self.step, 1.0 / 60.0)

    def step(self, dt):
        self.ship.step(dt)
        self.world.Step(dt, 10, 8)
        destroy_agents = set()
        for agent_1, agent_2 in self.contact_results:
            if (type(agent_1) is Shot and type(agent_2) is Asteroid or
                type(agent_1) is Asteroid and type(agent_2) is Shot):
                destroy_agents.add(agent_1)
                destroy_agents.add(agent_2)
        for agent in destroy_agents:
            if type(agent) is Asteroid:
                agent.split()
            self.world.DestroyBody(agent.body)
        del self.contact_results[:]
        
    def on_draw(self):
        glClearColor(0.0, 0.0, 0.0, 0.0)
        self.clear()
        glPushMatrix()
        glTranslated(self.width / 2.0, self.height / 2.0, 0.0)
        glScaled(15.0, 15.0, 15.0)
        position = self.ship.body.GetPosition()
        glTranslated(-position.x, -position.y, 0.0)
        self.draw_lifeline()
        self.draw_towline()
        for agent in self.query_draw():
            agent.draw()
        glPopMatrix()

    def query_draw(self):
        position = self.ship.body.GetPosition()
        aabb = box2d.b2AABB()
        aabb.lowerBound.Set(position.x - 40.0, position.y - 25.0)
        aabb.upperBound.Set(position.x + 40.0, position.y + 25.0)
        max_count = 100
        (count, shapes) = self.world.Query(aabb, max_count)
        agents = set(shape.GetBody().GetUserData() for shape in shapes)
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

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            sys.exit()
        if symbol == pyglet.window.key.UP:
            self.ship.thrust = 1.0
        if symbol == pyglet.window.key.DOWN:
            self.ship.thrust = -0.5
        if symbol == pyglet.window.key.SPACE:
            self.ship.firing = True
        if symbol == pyglet.window.key.LEFT:
            self.ship.turn = 1.0
        if symbol == pyglet.window.key.RIGHT:
            self.ship.turn = -1.0
        if symbol == pyglet.window.key.ENTER:
            self.ship.toggle_towline()

    def on_key_release(self, symbol, modifiers):
        if symbol == pyglet.window.key.UP:
            self.ship.thrust = 0.0
        if symbol == pyglet.window.key.SPACE:
            self.ship.firing = False
        if symbol in (pyglet.window.key.LEFT, pyglet.window.key.RIGHT):
            self.ship.turn = 0.0

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

def main():
    window = VoidWindow()
    pyglet.app.run()
    
if __name__ == '__main__':
    main()
