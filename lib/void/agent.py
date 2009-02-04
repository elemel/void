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

import math
from pyglet.gl import *

class Agent(object):
    def draw(self):
        position = self.body.GetPosition()
        angle = self.body.GetAngle()
        shape = self.body.GetShapeList()
        polygon = shape.asPolygon()
        glPushMatrix()
        glTranslated(position.x, position.y, 0.0)
        glRotated(angle * 180.0 / math.pi, 0.0, 0.0, 1.0)
        glBegin(GL_POLYGON)
        glColor3d(*self.color)
        for x, y in polygon.getCoreVertices_tuple():
            glVertex2d(x, y)
        glEnd()
        glPopMatrix()
