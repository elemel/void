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
from itertools import izip
from math import sqrt

class  Vector(object):
    def __init__(self, iterable):
        self.__comps = tuple(iterable)
        
    @property
    def x(self):
        return self.__comps[0]

    @property
    def y(self):
        return self.__comps[1]

    @property
    def z(self):
        return self.__comps[2]
        
    def __add__(self, other):
        return Vector(x + y for x, y in izip(self, other))

    def __sub__(self, other):
        return Vector(x - y for x, y in izip(self, other))

    def __mul__(self, other):
        return Vector(x * other for x in self)

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        return Vector(x / other for x in self)
        
    def __neg__(self):
        return Vector(-x for x in self)
        
    def __iter__(self):
        return iter(self.__comps)
        
    def __abs__(self):
        return sqrt(sum(x ** 2 for x in self))
    
    def __len__(self):
        return len(self.__comps)
    
    def __getitem__(self, index):
        return self.__comps[index]
    
    @property
    def unit(self):
        return self / abs(self)
