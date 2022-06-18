#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import time
import pygame
import threading
import random
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

RG_CUBE_COUNT = 1000

# [RG] Recommended way to open files:
with open("./words.txt", 'r') as word_file:
	words = word_file.readlines()
stripped = map(str.strip, words)
valid_words = []
for w in stripped:
	test = re.findall('^[a-z]+$', w.lower())
	if test:
		# [RG] The indexing at the end avoids having each word in its own list.
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

## A list of strings is totally inappropriate, use [RG] tuples.
# voxels = ['0,0,0','0,1,0','0,2,0','0,3,0','1,0,0','1,1,0','1,2,0','1,3,0','2,0,0','2,1,0','2,2,0','2,3,0','3,0,0','3,1,0','3,2,0','3,3,0',
#               '0,0,1','0,1,1','0,2,1','0,3,1','1,0,1','1,1,1','1,2,1','1,3,1','2,0,1','2,1,1','2,2,1','2,3,1','3,0,1','3,1,1','3,2,1','3,3,1',
#               '0,0,2','0,1,2','0,2,2','0,3,2','1,0,2','1,1,2','1,2,2','1,3,2','2,0,2','2,1,2','2,2,2','2,3,2','3,0,2','3,1,2','3,2,2','3,3,2',
#               '0,0,3','0,1,3','0,2,3','0,3,3','1,0,3','1,1,3','1,2,3','1,3,3','2,0,3','2,1,3','2,2,3','2,3,3','3,0,3','3,1,3','3,2,3','3,3,3']

# [RG] List comprehension works nicely here.                                                                                                  
voxels = [ (i,j,k) for i in range(4) for j in range(4) for k in range(4)]

voxels_gl = ((.0,.0,.0),(.0,.1,.0),(.0,.2,.0),(.0,.3,.0),(.1,.0,.0),(.1,.1,.0),(.1,.2,.0),(.1,.3,.0),(.2,.0,.0),(.2,.1,.0),(.2,.2,.0),(.2,.3,.0),(.3,.0,.0),(.3,.1,.0),(.3,.2,.0),(.3,.3,.0),
             (.0,.0,.1),(.0,.1,.1),(.0,.2,.1),(.0,.3,.1),(.1,.0,.1),(.1,.1,.1),(.1,.2,.1),(.1,.3,.1),(.2,.0,.1),(.2,.1,.1),(.2,.2,.1),(.2,.3,.1),(.3,.0,.1),(.3,.1,.1),(.3,.2,.1),(.3,.3,.1),
             (.0,.0,.2),(.0,.1,.2),(.0,.2,.2),(.0,.3,.2),(.1,.0,.2),(.1,.1,.2),(.1,.2,.2),(.1,.3,.2),(.2,.0,.2),(.2,.1,.2),(.2,.2,.2),(.2,.3,.2),(.3,.0,.2),(.3,.1,.2),(.3,.2,.2),(.3,.3,.2),
             (.0,.0,.3),(.0,.1,.3),(.0,.2,.3),(.0,.3,.3),(.1,.0,.3),(.1,.1,.3),(.1,.2,.3),(.1,.3,.3),(.2,.0,.3),(.2,.1,.3),(.2,.2,.3),(.2,.3,.3),(.3,.0,.3),(.3,.1,.3),(.3,.2,.3),(.3,.3,.3))

# [RG] optimized to "bosephus mode".
def find_neighbors(cube, voxel):
	neighbors = []
	for vn in voxel_neighbors:
		voxel_neighbor = tuple(vn[i] + voxel[i] for i in range(3))
		neighbors.append(voxel_neighbor)
	neighboring_cubies = {}
	for n in neighbors:
		try:
			## Slow
			# neighboring_cubies.update({ n : cube[n] })
			## [RG] Faster
			neighboring_cubies[n] = cube[n]
		except KeyError:
			# neighboring_cubies.update( { n : None } )
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
	glEnable(GL_LINE_SMOOTH)
	glLineWidth(1)
	glBegin(GL_LINE_STRIP)
	lock.acquire()
	for voxel in walkabout_gl:
		glVertex3fv(tuple([float(a)/10 for a in voxel]))
		letters += cube[voxel]
	lock.release()
	glEnd()
	# glut_print(50, 50, GLUT_BITMAP_HELVETICA_18, letters, 1.0, 1.0, 1.0, 1.0 )
	glut_print(50, 50, GLUT_BITMAP_HELVETICA_18, str(word_count[cube_index]) + ': ' + letters, 1.0, 1.0, 1.0, 1.0 )

def render_gl():
	global speed
	pygame.display.init()
	glutInit()
	# screen = pygame.display.set_mode((1024, 768), OPENGL)
	screen = pygame.display.set_mode((1024, 768), DOUBLEBUF|OPENGL)
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

global word_count
word_count = [0] * 1000
cube_index = 0

# [RG] This is the recommended way to open files: no explicit "close" call necessary.
with open("./cubes.txt",'r') as cube_file:
	cubes = cube_file.readlines()

# [RG] Single line list comprehension instead of iteration.
boggle_boards = [x.lower() for x in map(str.strip, cubes[:RG_CUBE_COUNT])]

#for b in random.sample(boggle_boards, 1):
# 951 is the index that has the most words (3340)
for b in [boggle_boards[951]]:
	letters =  list(b)
	cube = {k:v for k, v in zip(voxels, letters)}
	for valid_word in valid_words:
		if not tCube.is_alive():
			quit()
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
	cube_index += 1

