#!/usr/bin/env python
#
#       RC4, ARC4, ARCFOUR algorithm
#
#       Copyright (c) 2009 joonis new media
#       Author: Thimo Kraemer <thimo.kraemer@joonis.de>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#
import base64
from os import urandom

try:
    range = xrange
    bord = ord
    to_string = lambda x : x
    to_bytestring = to_string 
except NameError:
    bord = lambda x : x
    to_string = lambda x : x.decode()
    to_bytestring = lambda x : x.encode()

__all__ = ['rc4crypt','encrypt','decrypt']



def _rc4crypt(data, box):
    x = 0
    y = 0
    for char in to_string(data):
        x = (x + 1) % 256
        y = (y + box[x]) % 256
        box[x], box[y] = box[y], box[x]
        yield chr(ord(char) ^ box[(box[x] + box[y]) % 256])
        

def rc4crypt(data, key):
    '''data and key must be a byte strings'''
    x = 0
    box = list(range(256))
    for i in range(256):
        x = (x + box[i] + bord(key[i % len(key)])) % 256
        box[i], box[x] = box[x], box[i]
    v = ''.join(_rc4crypt(data,box))
    return to_bytestring(v)


def encrypt(plaintext, key, salt_size = 8):
    if not plaintext:
        return ''
    salt = urandom(salt_size)
    v = rc4crypt(plaintext,salt + key)
    n = to_bytestring(chr(salt_size))
    rs = n+salt+v
    return base64.b64encode(rs)


def decrypt(ciphertext, key):
    if ciphertext:
        rs = base64.b64decode(ciphertext)
        sl = bord(rs[0])+1
        salt = rs[1:sl]
        ciphertext = rs[sl:]
        return rc4crypt(ciphertext,salt+key)
    else:
        return ''
