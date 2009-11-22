# -*- coding: utf-8 -*-

# Copyright © 2009 Alessandro Morandi (email : webmaster@simbul.net)
#
# This file is part of pymeo.
# 
# pymeo is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# pymeo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with pymeo.  If not, see <http://www.gnu.org/licenses/>.

from distutils.core import setup

setup(
    name='Pymeo',
    version='0.1',
    description='Python wrapper for Vimeo Advanced APIs',
    author='Alessandro Morandi',
    author_email='webmaster@simbul.net',
    packages=['pymeo'],
    install_requires=['oauth'],
)