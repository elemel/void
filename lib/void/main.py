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

class Body(object):
    radius = 1.0
    max_rotation_speed = 10.0

    def __init__(self, groups, created_at):
        self.pos = numpy.array([0.0, 0.0])
        self.created_at = created_at
        self.velocity = numpy.array([0.0, 0.0])
        self.rotation = 0.0
        self.rotation_speed = 0.0

    def update(self, delta_time):
        self.pos += self.velocity * delta_time
        self.rotation += self.rotation_speed * delta_time

    def draw(self):
        x, y = self.pos
        glPushMatrix()
        glTranslated(x, y, 0.0)
        glRotated((self.rotation * 180.0) / math.pi - 90.0, 0.0, 0.0, 1.0)
        self.draw_geometry()
        glPopMatrix()

    def draw_geometry(self):
        pass

class Asteroid(Body):
    radius = 2.0
    max_velocity = 3.0
    color = [0.0, 0.0, 1.0]
    vertices = [[-2.0, -2.0], [2.0, -2.0], [0.0, 2.0]]

    @staticmethod
    def generate(groups, time):
        asteroid = Asteroid(groups, time)
        asteroid.color = [0.5 * random.random(), 0.5 * random.random(),
                          0.5 + 0.5 * random.random()]
        asteroid.radius = 3.0 + 3.0 * random.random()

        # Generate 4-5 angles as a sorted list.
        angles = [math.pi * 2.0 * random.random()
                  for _ in xrange(random.randrange(4, 6))]
        angles.sort()
        
        # Smooth angles by averaging them with a perfect polygon.
        step = math.pi * 2.0 / len(angles)
        for i in xrange(len(angles)):
            angles[i] = (angles[i] + i * step) / 2.0

        asteroid.vertices = [(math.cos(a) * asteroid.radius,
                              math.sin(a) * asteroid.radius) for a in angles]
        return asteroid

    def draw_geometry(self):
        glBegin(GL_POLYGON)
        glColor3d(*self.color)
        for vertex in self.vertices:
            glVertex2d(*vertex)
        glEnd()

class Plasma(Body):
    radius = 0.1
    max_velocity = 20.0

    def draw_geometry(self):
        glBegin(GL_QUADS)
        glColor3d(1.0, 0.0, 0.0)
        glVertex2d(-0.1, -0.1)
        glVertex2d(-0.1, 0.1)
        glVertex2d(0.1, 0.1)
        glVertex2d(0.1, -0.1)
        glEnd()

class VoidWindow(pyglet.window.Window):
    def __init__(self):
        pyglet.window.Window.__init__(self, fullscreen=True, caption="Void")
        world_aabb = box2d.b2AABB()
        world_aabb.lowerBound.Set(-100.0, -100.0)
        world_aabb.upperBound.Set(100.0, 100.0)
        gravity = box2d.b2Vec2(0.0, 0.0)
        self.world = box2d.b2World(world_aabb, gravity, False)
        ship_body_def = box2d.b2BodyDef()
        ship_body_def.position.Set(0.0, 0.0)
        self.ship_body = self.world.CreateBody(ship_body_def)
        ship_shape_def = box2d.b2PolygonDef()
        ship_shape_def.setVertices_tuple([(-1.0, -1.0), (1.0, -1.0),
                                          (0.0, 2.0)])
        ship_shape_def.density = 1.0
        self.ship_body.CreateShape(ship_shape_def)
        self.ship_body.SetMassFromShapes()
        self.ship_thrusting = False
        self.ship_firing = False
        self.ship_max_angular_velocity = 2.0 * math.pi
        pyglet.clock.schedule_interval(self.update, 1.0 / 60.0)
        self.asteroids = []
        for _ in xrange(20):
            self.asteroids.append(self.generate_asteroid())

    def update(self, dt):
        if self.ship_thrusting:
            angle = self.ship_body.GetAngle()
            force = 50.0 * box2d.b2Vec2(math.cos(angle), math.sin(angle))
            point = self.ship_body.GetPosition()
            self.ship_body.ApplyForce(force, point)
        self.world.Step(dt, 10, 8)
        for asteroid in self.asteroids:
            asteroid.update(dt)
        
    def on_draw(self):
        glClearColor(0.0, 0.0, 0.0, 0.0)
        self.clear()
        glPushMatrix()
        glTranslated(self.width / 2.0, self.height / 2.0, 0.0)
        glScaled(15.0, 15.0, 15.0)
        position = self.ship_body.GetPosition()
        glTranslated(-position.x, -position.y, 0.0)
        ship_shape = self.ship_body.GetShapeList()
        polygon = ship_shape.asPolygon()
        glPushMatrix()
        glTranslated(position.x, position.y, 0.0)
        glRotated((self.ship_body.GetAngle() * 180.0) / math.pi - 90.0,
                  0.0, 0.0, 1.0)
        glBegin(GL_TRIANGLES)
        glColor3d(0.0, 1.0, 0.0)
        for x, y in polygon.getCoreVertices_tuple():
            glVertex2d(x, y)
        glEnd()
        glPopMatrix()
        for asteroid in self.asteroids:
            asteroid.draw()
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

    def generate_asteroid(self):
        asteroid = Asteroid.generate([], 0.0)
        angle = 2.0 * math.pi * random.random()
        dist = 15.0 + 15.0 * random.random()
        asteroid.pos = dist * numpy.array([math.cos(angle), math.sin(angle)])
        if asteroid.pos.any():
            unit = asteroid.pos / numpy.linalg.norm(asteroid.pos)
            asteroid.velocity = (-unit * asteroid.max_velocity *
                                 (0.5 + 0.5 * random.random()))
        else:
            asteroid.velocity = numpy.array([0.0, 0.0])
        asteroid.rotation = random.random() * 2.0 * math.pi
        asteroid.rotation_speed = (-1.0 + 2.0 * random.random()) * 1.0
        return asteroid

def main():
    window = VoidWindow()
    pyglet.app.run()
    
if __name__ == '__main__':
    main()
