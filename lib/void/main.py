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
import Box2D2 as box2d
from pyglet.gl import *

class VoidWindow(pyglet.window.Window):
    def __init__(self):
        pyglet.window.Window.__init__(self, fullscreen=True, caption="Void")
        self.set_mouse_visible(False)
        self.create_world()
        self.create_ship_body()
        self.asteroid_bodies = []
        for _ in xrange(10):
            self.create_asteroid_body()
        self.ship_thrusting = False
        self.ship_firing = False
        self.ship_max_angular_velocity = 2.0 * math.pi
        pyglet.clock.schedule_interval(self.update, 1.0 / 60.0)

    def update(self, dt):
        if self.ship_thrusting:
            angle = self.ship_body.GetAngle()
            force = 100.0 * box2d.b2Vec2(-math.sin(angle), math.cos(angle))
            point = self.ship_body.GetPosition()
            self.ship_body.ApplyForce(force, point)
        self.world.Step(dt, 10, 8)
        
    def on_draw(self):
        glClearColor(0.0, 0.0, 0.0, 0.0)
        self.clear()
        glPushMatrix()
        glTranslated(self.width / 2.0, self.height / 2.0, 0.0)
        glScaled(15.0, 15.0, 15.0)
        position = self.ship_body.GetPosition()
        glTranslated(-position.x, -position.y, 0.0)
        self.draw_ship()
        self.draw_asteroids()
        glPopMatrix()

    def draw_ship(self):
        self.draw_body(self.ship_body, (1.0, 1.0, 1.0))

    def draw_asteroids(self):
        for asteroid_body in self.asteroid_bodies:
            color = asteroid_body.GetUserData()
            self.draw_body(asteroid_body, color)

    def draw_body(self, body, color):
        position = body.GetPosition()
        angle = body.GetAngle()
        shape = body.GetShapeList()
        polygon = shape.asPolygon()
        glPushMatrix()
        glTranslated(position.x, position.y, 0.0)
        glRotated(angle * 180.0 / math.pi, 0.0, 0.0, 1.0)
        glBegin(GL_POLYGON)
        glColor3d(*color)
        for x, y in polygon.getCoreVertices_tuple():
            glVertex2d(x, y)
        glEnd()
        glPopMatrix()

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            sys,exit()
        if symbol == pyglet.window.key.UP:
            self.ship_thrusting = True
        if symbol == pyglet.window.key.SPACE:
            self.ship_firing = True
        if symbol == pyglet.window.key.LEFT:
            self.ship_body.SetAngularVelocity(self.ship_max_angular_velocity)
        if symbol == pyglet.window.key.RIGHT:
            self.ship_body.SetAngularVelocity(-self.ship_max_angular_velocity)

    def on_key_release(self, symbol, modifiers):
        if symbol == pyglet.window.key.UP:
            self.ship_thrusting = False
        if symbol == pyglet.window.key.SPACE:
            self.ship_firing = False
        if symbol in (pyglet.window.key.LEFT, pyglet.window.key.RIGHT):
            self.ship_body.SetAngularVelocity(0.0)

    def create_world(self):
        world_aabb = box2d.b2AABB()
        world_aabb.lowerBound.Set(-200.0, -200.0)
        world_aabb.upperBound.Set(200.0, 200.0)
        gravity = box2d.b2Vec2(0.0, 0.0)
        self.world = box2d.b2World(world_aabb, gravity, False)

    def create_ship_body(self):
        ship_body_def = box2d.b2BodyDef()
        ship_body_def.position.Set(0.0, 0.0)
        self.ship_body = self.world.CreateBody(ship_body_def)
        ship_shape_def = box2d.b2PolygonDef()
        ship_shape_def.setVertices_tuple([(-1.0, -1.0), (1.0, -1.0),
                                          (0.0, 2.0)])
        ship_shape_def.density = 2.0
        ship_shape_def.restitution = 1.0
        self.ship_body.CreateShape(ship_shape_def)
        self.ship_body.SetMassFromShapes()

    def create_asteroid_body(self):
        angle = 2.0 * math.pi * random.random()
        distance = 15.0 + 15.0 * random.random()
        x = distance * math.cos(angle)
        y = distance * math.sin(angle)
        asteroid_body_def = box2d.b2BodyDef()
        asteroid_body_def.position.Set(x, y)
        asteroid_body = self.world.CreateBody(asteroid_body_def)
        asteroid_shape_def = box2d.b2PolygonDef()
        radius = 2.0 + 5.0 * random.random()
        vertices = []
        for i in xrange(5):
            angle = (i + random.random()) / 5.0 * 2.0 * math.pi
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            vertices.append((x, y))
        asteroid_shape_def.setVertices_tuple(vertices)
        asteroid_shape_def.density = 4.0 + random.random()
        asteroid_shape_def.restitution = 1.0
        asteroid_body.CreateShape(asteroid_shape_def)
        asteroid_body.SetMassFromShapes()
        asteroid_body.SetLinearVelocity(box2d.b2Vec2(2.0 * random.random(),
                                                     2.0 * random.random()))
        asteroid_body.SetAngularVelocity(math.pi * (random.random() - 0.5))
        color = (0.5 * random.random(),
                 0.5 * random.random(),
                 0.5 * random.random() + 0.5)
        asteroid_body.SetUserData(color)
        self.asteroid_bodies.append(asteroid_body)

def main():
    window = VoidWindow()
    pyglet.app.run()
    
if __name__ == '__main__':
    main()
