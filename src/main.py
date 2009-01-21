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

from __future__ import division
import pygame, sys, random, math, os, numpy

class Transform(object):
    def __init__(self, offset, scale):
        self.offset = offset
        self.scale = scale

class Body(pygame.sprite.Sprite):
    radius = 1.0
    max_rotation_speed = 10.0

    def __init__(self, groups, created_at):
        pygame.sprite.Sprite.__init__(self, *groups)
        self.pos = numpy.array([0.0, 0.0])
        self.created_at = created_at
        self.velocity = numpy.array([0.0, 0.0])
        self.rotation = 0.0
        self.rotation_speed = 0.0

    def update(self, delta_time):
        self.pos += self.velocity * delta_time
        self.rotation += self.rotation_speed * delta_time

    @property
    def rect(self):
        return pygame.Rect(self.pos[0] - self.radius, self.pos[1] - self.radius,
                           self.radius * 2.0, self.radius * 2.0)

    def draw_with_transform(self, dest, transform):
        self.draw_image(dest, transform)
        self.draw_circle(dest, transform)
        
    def draw_image(self, dest, transform):
        image = pygame.transform.rotate(self.image,
                                        self.rotation * 180.0 / math.pi)
        image_width, image_height = image.get_size()
        display_width, display_height = dest.get_size()
        x, y = (self.pos + transform.offset) * transform.scale
        x = int((display_width - image_width) // 2 + x)
        y = int((display_height - image_height) // 2 - y)
        dest.blit(image, (x, y))

    def draw_circle(self, dest, transform):
        display_width, display_height = dest.get_size()
        x, y = (self.pos + transform.offset) * transform.scale
        x = display_width // 2 + x
        y = display_height // 2 - y
        radius = int(self.radius * transform.scale)
        center = int(x), int(y)
        pygame.draw.circle(dest, pygame.color.Color('red'), center, radius, 3)

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
        if (self.firing and
            self.fired_at + self.cooldown < pygame.time.get_ticks() / 1000.0):
            direction = numpy.array([math.cos(self.rotation),
                                     math.sin(self.rotation)])
            shot = self.create_shot()
            shot.pos = self.pos + direction * self.gun_pos
            shot.rotation = self.rotation
            shot.velocity = self.velocity + self.shot_velocity * direction
            self.fired_at = pygame.time.get_ticks() / 1000.0

class Asteroid(Body):
    radius = 2.0
    max_velocity = 3.0

class Plasma(Body):
    radius = 0.1
    max_velocity = 20.0

class Game(object):
    def __init__(self, images):
        self.images = images
        self.bodies = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.shots = pygame.sprite.Group()
        def create_shot():
            shot = Plasma([self.shots, self.bodies], self.time)
            shot.image = images['plasma']
            return shot
        self.player_ship = Ship([self.player_group, self.bodies],
                                self.time, create_shot)
        self.player_ship.image = images['ship']
        for _ in xrange(10):
            self.create_asteroid()
        
    def create_asteroid(self):
        asteroid = Asteroid([self.asteroids, self.bodies], self.time)
        asteroid.image = self.images['asteroid']
        angle = (random.random() - 0.5) * math.pi
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

    def update(self, delta_time):
        self.bodies.update(delta_time)
        pygame.sprite.groupcollide(self.shots, self.asteroids, True, True)
        if pygame.sprite.spritecollideany(self.player_ship, self.asteroids):
            sys.exit()

    def draw_with_transform(self, dest, transform):
        for body in self.bodies:
            body.draw_with_transform(dest, transform)

    @property
    def time(self):
        return pygame.time.get_ticks() / 1000.0

def init_display():
    pygame.display.init()
    resolution = pygame.display.list_modes()[0]
    display_surface = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
    return display_surface

def load_image(file_name):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    root = os.getenv('VOID_ROOT', root)
    file_name = os.path.join(root, 'data', file_name)
    image = pygame.image.load(file_name)
    image.convert_alpha()
    return image

def load_images():
    images = {}
    images['ship'] = load_image("ship.png")
    images['asteroid'] = load_image("asteroid.png")
    images['plasma'] = load_image("plasma.png")
    return images

def apply_player_ship_constraints(player_ship, game):
    velocity_mag = numpy.linalg.norm(player_ship.velocity)
    if velocity_mag > player_ship.max_velocity:
        player_ship.velocity /= velocity_mag
        player_ship.velocity *= player_ship.max_velocity

def main():
    pygame.init()
    pygame.mouse.set_visible(False)
    display_surface = init_display()
    images = load_images()
    game = Game(images)
    quit = False
    old_time = pygame.time.get_ticks()
    time_step = 20
    scale = 50.0
    while not quit:
        for event in pygame.event.get():
            if (event.type == pygame.QUIT or
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                quit = True
        while old_time + time_step < pygame.time.get_ticks():
            pressed = pygame.key.get_pressed()
            game.player_ship.thrusting = pressed[pygame.K_UP]
            if pressed[pygame.K_LEFT]:
                game.player_ship.rotation_speed = \
                    game.player_ship.max_rotation_speed
            elif pressed[pygame.K_RIGHT]:
                game.player_ship.rotation_speed = \
                    -game.player_ship.max_rotation_speed
            else:
                game.player_ship.rotation_speed = 0.0
            game.player_ship.firing = pressed[pygame.K_SPACE]
            game.update(time_step / 1000.0)
            apply_player_ship_constraints(game.player_ship, game)
            old_time += time_step
        display_surface.fill(pygame.color.Color('black'))
        transform = Transform(-game.player_ship.pos, scale)
        game.draw_with_transform(display_surface, transform)
        pygame.display.flip()
    
if __name__ == '__main__':
    main()
