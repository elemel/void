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

import sys, pyglet
from pyglet.gl import *
from void.game import Game

class GameScreen(object):
    def __init__(self, window):
        self.window = window
        self.game = Game()

    def step(self, dt):
        self.game.step(dt)

    def on_draw(self):
        glPushMatrix()
        glTranslated(self.window.width / 2.0, self.window.height / 2.0, 0.0)
        self.game.on_draw()
        glPopMatrix()

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            self.window.pop_screen()
        if symbol == pyglet.window.key.UP:
            self.game.ship.thrust = 1.0
        if symbol == pyglet.window.key.DOWN:
            self.game.ship.thrust = -0.5
        if symbol == pyglet.window.key.SPACE:
            self.game.ship.firing = True
        if symbol == pyglet.window.key.LEFT:
            self.game.ship.turn = 1.0
        if symbol == pyglet.window.key.RIGHT:
            self.game.ship.turn = -1.0
        if symbol == pyglet.window.key.ENTER:
            self.game.ship.toggle_towline()

    def on_key_release(self, symbol, modifiers):
        if symbol == pyglet.window.key.UP:
            self.game.ship.thrust = 0.0
        if symbol == pyglet.window.key.DOWN:
            self.game.ship.thrust = 0.0
        if symbol == pyglet.window.key.SPACE:
            self.game.ship.firing = False
        if symbol in (pyglet.window.key.LEFT, pyglet.window.key.RIGHT):
            self.game.ship.turn = 0.0
