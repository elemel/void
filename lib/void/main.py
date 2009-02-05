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
from void.ship import Ship

class VoidWindow(pyglet.window.Window):
    def __init__(self):
        pyglet.window.Window.__init__(self, fullscreen=True, caption="Void")
        self.set_mouse_visible(False)
        self.world = self.create_world()
        self.shots = []
        self.ship = Ship(self.world, self.shots)
        self.asteroids = []
        for _ in xrange(20):
            self.asteroids.append(Asteroid(self.world))
        pyglet.clock.schedule_interval(self.step, 1.0 / 60.0)

    def step(self, dt):
        self.ship.step(dt)
        self.world.Step(dt, 10, 8)
        
    def on_draw(self):
        glClearColor(0.0, 0.0, 0.0, 0.0)
        self.clear()
        glPushMatrix()
        glTranslated(self.width / 2.0, self.height / 2.0, 0.0)
        glScaled(15.0, 15.0, 15.0)
        position = self.ship.body.GetPosition()
        glTranslated(-position.x, -position.y, 0.0)
        for shot in self.shots:
            shot.draw()
        self.ship.draw()
        for asteroid in self.asteroids:
            asteroid.draw()
        glPopMatrix()

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            sys.exit()
        if symbol == pyglet.window.key.UP:
            self.ship.thrusting = True
        if symbol == pyglet.window.key.SPACE:
            self.ship.firing = True
        if symbol == pyglet.window.key.LEFT:
            self.ship.turning = 1.0
        if symbol == pyglet.window.key.RIGHT:
            self.ship.turning = -1.0

    def on_key_release(self, symbol, modifiers):
        if symbol == pyglet.window.key.UP:
            self.ship.thrusting = False
        if symbol == pyglet.window.key.SPACE:
            self.ship.firing = False
        if symbol in (pyglet.window.key.LEFT, pyglet.window.key.RIGHT):
            self.ship.turning = 0.0

    def create_world(self):
        world_aabb = box2d.b2AABB()
        world_aabb.lowerBound.Set(-200.0, -200.0)
        world_aabb.upperBound.Set(200.0, 200.0)
        gravity = box2d.b2Vec2(0.0, 0.0)
        return box2d.b2World(world_aabb, gravity, False)

def main():
    window = VoidWindow()
    pyglet.app.run()
    
if __name__ == '__main__':
    main()
