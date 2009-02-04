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
import void.box2d as box2d
from void.ship import Ship

class VoidWindow(pyglet.window.Window):
    def __init__(self):
        pyglet.window.Window.__init__(self, fullscreen=True, caption="Void")
        self.set_mouse_visible(False)
        self.world = self.create_world()
        self.ship = Ship(self.world)
        self.shot_bodies = []
        self.asteroid_bodies = []
        for _ in xrange(20):
            self.create_asteroid_body()
        pyglet.clock.schedule_interval(self.update, 1.0 / 60.0)

    def update(self, dt):
        if self.ship.thrusting:
            angle = self.ship.body.GetAngle()
            force = 100.0 * box2d.b2Vec2(-math.sin(angle), math.cos(angle))
            point = self.ship.body.GetPosition()
            self.ship.body.ApplyForce(force, point)
        self.ship.cooldown -= dt
        if self.ship.firing and self.ship.cooldown <= 0.0:
            self.create_shot_body()
            self.ship.cooldown = 0.1
        self.world.Step(dt, 10, 8)
        
    def on_draw(self):
        glClearColor(0.0, 0.0, 0.0, 0.0)
        self.clear()
        glPushMatrix()
        glTranslated(self.width / 2.0, self.height / 2.0, 0.0)
        glScaled(15.0, 15.0, 15.0)
        position = self.ship.body.GetPosition()
        glTranslated(-position.x, -position.y, 0.0)
        self.draw_shots()
        self.draw_ship()
        self.draw_asteroids()
        glPopMatrix()

    def draw_ship(self):
        self.draw_body(self.ship.body, (1.0, 1.0, 1.0))

    def draw_shots(self):
        for shot_body in self.shot_bodies:
            self.draw_body(shot_body, (1.0, 0.0, 0.0))

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
            sys.exit()
        if symbol == pyglet.window.key.UP:
            self.ship.thrusting = True
        if symbol == pyglet.window.key.SPACE:
            self.ship.firing = True
        if symbol == pyglet.window.key.LEFT:
            self.ship.body.SetAngularVelocity(self.ship.max_angular_velocity)
        if symbol == pyglet.window.key.RIGHT:
            self.ship.body.SetAngularVelocity(-self.ship.max_angular_velocity)

    def on_key_release(self, symbol, modifiers):
        if symbol == pyglet.window.key.UP:
            self.ship.thrusting = False
        if symbol == pyglet.window.key.SPACE:
            self.ship.firing = False
        if symbol in (pyglet.window.key.LEFT, pyglet.window.key.RIGHT):
            self.ship.body.SetAngularVelocity(0.0)

    def create_world(self):
        world_aabb = box2d.b2AABB()
        world_aabb.lowerBound.Set(-200.0, -200.0)
        world_aabb.upperBound.Set(200.0, 200.0)
        gravity = box2d.b2Vec2(0.0, 0.0)
        return box2d.b2World(world_aabb, gravity, False)

    def create_shot_body(self):
        angle = self.ship.body.GetAngle()
        shot_body_def = box2d.b2BodyDef()
        shot_body_def.position = self.ship.body.GetPosition()
        shot_body_def.angle = angle
        shot_body = self.world.CreateBody(shot_body_def)
        shot_shape_def = box2d.b2PolygonDef()
        shot_shape_def.setVertices_tuple([(-0.2, -0.2), (0.2, -0.2),
                                          (0.2, 0.2), (-0.2, 0.2)])
        shot_shape_def.density = 10.0
        shot_shape_def.restitution = 1.0
        shot_shape_def.filter.categoryBits = 0x0001
        shot_shape_def.filter.maskBits = 0x0002
        shot_body.CreateShape(shot_shape_def)
        shot_body.SetMassFromShapes()
        linear_velocity = (self.ship.body.GetLinearVelocity() +
                           10.0 * box2d.b2Vec2(-math.sin(angle), math.cos(angle)))
        shot_body.SetLinearVelocity(linear_velocity)
        self.shot_bodies.append(shot_body)

    def create_asteroid_body(self):
        angle = 2.0 * math.pi * random.random()
        distance = 15.0 + 15.0 * random.random()
        x = distance * math.cos(angle)
        y = distance * math.sin(angle)
        asteroid_body_def = box2d.b2BodyDef()
        asteroid_body_def.position.Set(x, y)
        asteroid_body_def.angle = 2.0 * math.pi * random.random()
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
        asteroid_shape_def.filter.categoryBits = 0x0002
        asteroid_shape_def.filter.maskBits = 0x0001
        asteroid_body.CreateShape(asteroid_shape_def)
        asteroid_body.SetMassFromShapes()
        linear_velocity = 3.0 * box2d.b2Vec2(random.random() - 0.5,
                                             random.random() - 0.5)
        asteroid_body.SetLinearVelocity(linear_velocity)
        asteroid_body.SetAngularVelocity(random.random() - 0.5)
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
