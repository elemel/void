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

class Ship(Body):
    radius = 1.0
    max_velocity = 10.0
    max_rotation_speed = 5.0
    shot_velocity = 10.0
    gun_pos = 1.5
    max_thrust = 0.5

    def __init__(self, groups, created_at, create_shot):
        Body.__init__(self, groups, created_at)
        self.create_shot = create_shot
        self.thrusting = False
        self.firing = False
        self.cooldown = 0.2
        self.fired_at = 0.0

    def update(self, delta_time):
        Body.update(self, delta_time)
        self.update_velocity(delta_time)
        self.update_cannon(delta_time)
        
    def update_velocity(self, delta_time):
        self.velocity += (self.thrusting * self.max_thrust
                          * numpy.array([math.cos(self.rotation),
                                         math.sin(self.rotation)]))

    def update_cannon(self, delta_time):
        pass

    def draw_geometry(self):
        glBegin(GL_TRIANGLES)
        glColor3d(0.0, 1.0, 0.0)
        glVertex2d(-0.5, -1.0)
        glVertex2d(0.0, 1.0)
        glVertex2d(0.5, -1.0)
        glEnd()

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
        asteroid.radius = 1.5 + random.random()

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
        pyglet.window.Window.__init__(self, width=640, height=480,
                                      caption="Void")
        pyglet.clock.schedule_interval(self.update, 0.01)
        def create_shot():
            shot = Plasma([], 0.0)
            return shot
        self.player_ship = Ship([], 0.0, create_shot)
        self.asteroids = []
        for _ in xrange(10):
            self.asteroids.append(self.generate_asteroid())

    def update(self, dt):
        self.player_ship.update(dt)
        for asteroid in self.asteroids:
            asteroid.update(dt)
        self.apply_player_ship_constraints()
        
    def on_draw(self):
        glClearColor(0.0, 0.0, 0.0, 0.0)
        self.clear()
        glPushMatrix()
        glTranslated(self.width / 2.0, self.height / 2.0, 0.0)
        glScaled(20.0, 20.0, 20.0)
        x, y = self.player_ship.pos
        glTranslated(-x, -y, 0.0)
        self.player_ship.draw()
        for asteroid in self.asteroids:
            asteroid.draw()
        glPopMatrix()

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            sys,exit()
        if symbol == pyglet.window.key.UP:
            self.player_ship.thrusting = True
        if symbol == pyglet.window.key.SPACE:
            self.player_ship.firing = True
        if symbol == pyglet.window.key.LEFT:
            self.player_ship.rotation_speed = \
                self.player_ship.max_rotation_speed
        if symbol == pyglet.window.key.RIGHT:
            self.player_ship.rotation_speed = \
                -self.player_ship.max_rotation_speed

    def on_key_release(self, symbol, modifiers):
        if symbol == pyglet.window.key.UP:
            self.player_ship.thrusting = False
        if symbol == pyglet.window.key.SPACE:
            self.player_ship.firing = False
        if symbol in (pyglet.window.key.LEFT, pyglet.window.key.RIGHT):
            self.player_ship.rotation_speed = 0.0

    def generate_asteroid(self):
        asteroid = Asteroid.generate([], 0.0)
        angle = random.random() * 2.0 * math.pi
        dist = random.random() * 10.0 + 10.0
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

    def apply_player_ship_constraints(self):
        velocity_mag = numpy.linalg.norm(self.player_ship.velocity)
        if velocity_mag > self.player_ship.max_velocity:
            self.player_ship.velocity *= (self.player_ship.max_velocity /
                                          velocity_mag)

def main():
    window = VoidWindow()
    pyglet.app.run()
    
if __name__ == '__main__':
    main()
