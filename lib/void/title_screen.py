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
from void.game_screen import GameScreen

class TitleScreen(object):
    def __init__(self, window):
        self.window = window
        self.void_label = pyglet.text.Label("Void", font_size=50.0, bold=True,
                                            anchor_x="center",
                                            anchor_y="center")
        self.play_label = pyglet.text.Label("[Enter] Play", font_size=20.0,
                                            anchor_x="center",
                                            anchor_y="center")
        self.exit_label = pyglet.text.Label("[Escape] Exit", font_size=20.0,
                                            anchor_x="center",
                                            anchor_y="center")

    def step(self, dt):
        pass

    def on_draw(self):
        glPushMatrix()
        glTranslated(self.window.width / 2.0, self.window.height * 2.0 / 3.0,
                     0.0)
        self.void_label.draw()
        glPopMatrix()

        glPushMatrix()
        glTranslated(self.window.width / 3.0, self.window.height / 3.0, 0.0)
        self.play_label.draw()
        glPopMatrix()

        glPushMatrix()
        glTranslated(self.window.width * 2.0 / 3.0, self.window.height / 3.0,
                     0.0)
        self.exit_label.draw()
        glPopMatrix()

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            self.window.pop_screen()
        if symbol == pyglet.window.key.ENTER:
            self.window.push_screen(GameScreen(self.window))

    def on_key_release(self, symbol, modifiers):
        pass

