#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import time
import numpy
import random
import pygame
import threading
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

cube_count = 1000
word_count = [0] * cube_count

with open("./cubes.txt",'r') as cube_file:
    cubes = cube_file.readlines()

with open("./words.txt", 'r') as word_file:
    words = word_file.readlines()

stripped = map(str.strip, words)
valid_words = []
for w in stripped:
    test = re.findall('^[a-z]+$', w.lower())
    if test:
        valid_words.append(test[0])

## https://github.com/bdrupieski/BoggleSolver/blob/master/BoggleSolver/BoggleSolver.cs
voxel_neighbors = [ (-1,-1,-1),(0,-1,-1),(1,-1,-1),
                    (-1, 0,-1),(0, 0,-1),(1, 0,-1),
                    (-1, 1,-1),(0, 1,-1),(1, 1,-1),
                    (-1,-1, 0),(0,-1, 0),(1,-1, 0),
                    (-1, 0, 0),          (1, 0, 0),
                    (-1, 1, 0),(0, 1, 0),(1, 1, 0),
                    (-1,-1, 1),(0,-1, 1),(1,-1, 1),
                    (-1, 0, 1),(0, 0, 1),(1, 0, 1),
                    (-1, 1, 1),(0, 1, 1),(1, 1, 1) ]

voxels = [(i,j,k) for i in range(4) for j in range(4) for k in range(4)]
voxels_gl = tuple((i,j,k) for i in numpy.arange(.0,.4,.1) for j in numpy.arange(.0,.4,.1) for k in numpy.arange(.0,.4,.1))

def find_neighbors(cube, voxel):
    neighbors = []
    for vn in voxel_neighbors:
        voxel_neighbor = tuple(vn[i] + voxel[i] for i in range(3))
        neighbors.append(voxel_neighbor)
    neighboring_cubies = {}
    for n in neighbors:
        try:
            neighboring_cubies[n] = cube[n]
        except KeyError:
            neighboring_cubies[n] = None
    for x in list(neighboring_cubies):
        if neighboring_cubies[x] is None:
            del neighboring_cubies[x]
    return neighboring_cubies

def arr2word(cube, voxels):
    word = ''
    for v in voxels:
        word += cube[v]
    return word

def find_voxels(cube, word, index, valid_word, voxel, walkabout):
    global walkabout_gl
    global speed
    walkabout.append(voxel)
    lock.acquire()
    walkabout_gl = walkabout
    lock.release()
    time.sleep(speed/10)
    index += 1
    try:
        next_letter = word[index]
    except IndexError:
        return walkabout
    neighborhood = find_neighbors(cube, voxel)
    for w in walkabout:
        r = neighborhood.get(w, None)
        if r:
            del neighborhood[w]
    voxels = [key for (key, value) in neighborhood.items() if value == next_letter]
    if voxels:
        for voxel in voxels:
            returned = find_voxels(cube, word, index, valid_word, voxel, walkabout)
            lock.acquire()
            walkabout_gl = returned
            lock.release()
            returned_word = arr2word(cube, returned)
            if returned_word == valid_word:
                return returned
            walkabout.pop()
    index -= 1
    return walkabout

## https://stackoverflow.com/questions/12837747/print-text-with-glut-and-python
def glut_print(x, y, font, text, r, g, b, a):
    blending = False
    if glIsEnabled(GL_BLEND):
        blending = True
    glColor3f(1,1,1)
    glWindowPos2f(x,y)
    for ch in text:
        glutBitmapCharacter(font, ctypes.c_int(ord(ch)))
    if not blending:
        glDisable(GL_BLEND)

def Cube():
    global walkabout_gl
    global cube
    letters = ''
    glColor3f(1.0,1.0,0.0)
    glEnable(GL_POINT_SMOOTH)
    glPointSize(5)
    glBegin(GL_POINTS)
    for voxel in voxels_gl:
        glVertex3fv(voxel)
    glEnd()
    glColor3f(1.0,0.0,0.0)
    glDisable(GL_LINE_SMOOTH)
    glDisable(GL_BLEND)
    glDisable(GL_LINE_STIPPLE)
    glDisable(GL_POINT_SMOOTH)
    glLineWidth(2.0)
    glBegin(GL_LINE_STRIP)
    lock.acquire()
    for voxel in walkabout_gl:
        glVertex3fv(tuple([float(a)/10 for a in voxel]))
        letters += cube[voxel]
    lock.release()
    glEnd()
    glut_print(50, 50, GLUT_BITMAP_HELVETICA_18, str(word_count[cube_index]) + ': ' +  letters, 1.0, 1.0, 1.0, 1.0 )

def render_gl():
    global speed
    pygame.display.init()
    glutInit()
    # screen = pygame.display.set_mode((800, 600), DOUBLEBUF|OPENGL)
    screen = pygame.display.set_mode((1024, 768), OPENGL)
    pygame.display.set_caption(u'Na\u00EFve Boggle Solver')
    clock = pygame.time.Clock()
    done = False
    gluPerspective(45, 4/3, 0.5, 50.0)
    glTranslatef(-0.8, -0.2, -5.0)
    glScalef(4.0, 4.0, 4.0)

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                done = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_KP_PLUS:
                if ( speed > 0 ):
                    speed -= 1
            if event.type == pygame.KEYDOWN and event.key == pygame.K_KP_MINUS:
                speed += 1

        glRotatef(1, 3, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        Cube()
        pygame.display.flip()
        clock.tick(20)

    pygame.quit()
    quit()

lock = threading.Lock()
walkabout_gl = ''
tCube = threading.Thread(target=render_gl, name='tCube')
tCube.start()
speed = 1

cube_index = 0
boggle_boards = [x.lower() for x in map(str.strip, cubes[:cube_count])]

# for b in random.sample(boggle_boards, 1):

# 951 is the index that has the most words (3340)
for b in [boggle_boards[951]]:
    tfl = []
    letters = list(b)
    cube = {k:v for k, v in zip(voxels, letters)}
    for letter in letters:
        if letter not in tfl: tfl.append(letter)
        base_voxels = [key for (key, value) in cube.items() if value == letter]
        for voxel in base_voxels:
            neighborhood = find_neighbors(cube, voxel) 
            for neighbor in neighborhood:
                neighboring_letter = cube[neighbor]
                if letter+neighboring_letter not in tfl: tfl.append(letter+neighboring_letter)

    for valid_word in valid_words:
        if not tCube.is_alive():
            quit()
        if valid_word[:2] in tfl:
            array_word = list(valid_word)
            index = 0
            first_letter = array_word[index]
            base_voxels = [key for (key, value) in cube.items() if value == first_letter]
            for voxel in base_voxels:
                walkabout = []
                returned = find_voxels(cube, array_word, index, valid_word, voxel, walkabout)
                lock.acquire()
                walkabout_gl = returned
                lock.release()
                returned_word = arr2word(cube, returned)
                if returned_word == valid_word:
                    word_count[cube_index] += 1
                    break

    print(word_count[cube_index])
    # cube_index += 1
