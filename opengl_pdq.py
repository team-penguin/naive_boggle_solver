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

with open("./cubes.txt",'r') as cube_file:                                          
	cubes = cube_file.readlines()
with open("./words.txt", 'r') as word_file:
	words = word_file.readlines()

stripped = map(str.strip, words)
valid_words = []
for w in stripped:
	valid = re.findall('^[a-z]+$', w.lower())
	if valid:
		# [RG] The indexing at the end avoids having each word in its own list.
		valid_words.append(valid[0])

voxels = [ (i,j,k) for i in range(4) for j in range(4) for k in range(4) ]

## Creates weirdness: (0.0, 0.0, 0.30000000000000004)
# gl_voxels = tuple((i,j,k) for i in numpy.arange(.0,.4,.1) for j in numpy.arange(.0,.4,.1) for k in numpy.arange(.0,.4,.1))

gl_voxels = ( (.0,.0,.0),(.0,.1,.0),(.0,.2,.0),(.0,.3,.0),(.1,.0,.0),(.1,.1,.0),(.1,.2,.0),(.1,.3,.0),(.2,.0,.0),(.2,.1,.0),(.2,.2,.0),(.2,.3,.0),(.3,.0,.0),(.3,.1,.0),(.3,.2,.0),(.3,.3,.0),
              (.0,.0,.1),(.0,.1,.1),(.0,.2,.1),(.0,.3,.1),(.1,.0,.1),(.1,.1,.1),(.1,.2,.1),(.1,.3,.1),(.2,.0,.1),(.2,.1,.1),(.2,.2,.1),(.2,.3,.1),(.3,.0,.1),(.3,.1,.1),(.3,.2,.1),(.3,.3,.1),
              (.0,.0,.2),(.0,.1,.2),(.0,.2,.2),(.0,.3,.2),(.1,.0,.2),(.1,.1,.2),(.1,.2,.2),(.1,.3,.2),(.2,.0,.2),(.2,.1,.2),(.2,.2,.2),(.2,.3,.2),(.3,.0,.2),(.3,.1,.2),(.3,.2,.2),(.3,.3,.2),
              (.0,.0,.3),(.0,.1,.3),(.0,.2,.3),(.0,.3,.3),(.1,.0,.3),(.1,.1,.3),(.1,.2,.3),(.1,.3,.3),(.2,.0,.3),(.2,.1,.3),(.2,.2,.3),(.2,.3,.3),(.3,.0,.3),(.3,.1,.3),(.3,.2,.3),(.3,.3,.3) )

## Answer #4: https://stackoverflow.com/questions/7367770/how-to-flatten-or-index-3d-array-in-1d-array
#  Flat[ x * height * depth + y * depth + z ] = elements[x][y][z]
#  where [WIDTH][HEIGHT][DEPTH]
##
# flat_voxel = (voxel[0] * 4 * 4) + (voxel[1] * 4) + voxel[2]

flat_dictionary = { 0:[-1, -4, -5, -16, -17, -20, -21],
					1:[1, -1, -3, -4, -5, -15, -16, -17, -19, -20, -21],
					2:[1, -1, -3, -4, -5, -15, -16, -17, -19, -20, -21],
					3:[1, -3, -4, -15, -16, -19, -20],
					4:[4, 3, -1, -4, -5, -12, -13, -16, -17, -20, -21],
					5:[5, 4, 3, 1, -1, -3, -4, -5, -11, -12, -13, -15, -16, -17, -19, -20, -21],
					6:[5, 4, 3, 1, -1, -3, -4, -5, -11, -12, -13, -15, -16, -17, -19, -20, -21],
					7:[5, 4, 1, -3, -4, -11, -12, -15, -16, -19, -20],
					8:[4, 3, -1, -4, -5, -12, -13, -16, -17, -20, -21],
					9:[5, 4, 3, 1, -1, -3, -4, -5, -11, -12, -13, -15, -16, -17, -19, -20, -21],
					10:[5, 4, 3, 1, -1, -3, -4, -5, -11, -12, -13, -15, -16, -17, -19, -20, -21],
					11:[5, 4, 1, -3, -4, -11, -12, -15, -16, -19, -20],
					12:[4, 3, -1, -12, -13, -16, -17],
					13:[5, 4, 3, 1, -1, -11, -12, -13, -15, -16, -17],
					14:[5, 4, 3, 1, -1, -11, -12, -13, -15, -16, -17],
					15:[5, 4, 1, -11, -12, -15, -16],
					16:[16, 15, 12, 11, -1, -4, -5, -16, -17, -20, -21],
					17:[17, 16, 15, 13, 12, 11, 1, -1, -3, -4, -5, -15, -16, -17, -19, -20, -21],
					18:[17, 16, 15, 13, 12, 11, 1, -1, -3, -4, -5, -15, -16, -17, -19, -20, -21],
					19:[17, 16, 13, 12, 1, -3, -4, -15, -16, -19, -20],
					20:[20, 19, 16, 15, 12, 11, 4, 3, -1, -4, -5, -12, -13, -16, -17, -20, -21],
					21:[21, 20, 19, 17, 16, 15, 13, 12, 11, 5, 4, 3, 1, -1, -3, -4, -5, -11, -12, -13, -15, -16, -17, -19, -20, -21],
					22:[21, 20, 19, 17, 16, 15, 13, 12, 11, 5, 4, 3, 1, -1, -3, -4, -5, -11, -12, -13, -15, -16, -17, -19, -20, -21],
					23:[21, 20, 17, 16, 13, 12, 5, 4, 1, -3, -4, -11, -12, -15, -16, -19, -20],
					24:[20, 19, 16, 15, 12, 11, 4, 3, -1, -4, -5, -12, -13, -16, -17, -20, -21],
					25:[21, 20, 19, 17, 16, 15, 13, 12, 11, 5, 4, 3, 1, -1, -3, -4, -5, -11, -12, -13, -15, -16, -17, -19, -20, -21],
					26:[21, 20, 19, 17, 16, 15, 13, 12, 11, 5, 4, 3, 1, -1, -3, -4, -5, -11, -12, -13, -15, -16, -17, -19, -20, -21],
					27:[21, 20, 17, 16, 13, 12, 5, 4, 1, -3, -4, -11, -12, -15, -16, -19, -20],
					28:[20, 19, 16, 15, 4, 3, -1, -12, -13, -16, -17],
					29:[21, 20, 19, 17, 16, 15, 5, 4, 3, 1, -1, -11, -12, -13, -15, -16, -17],
					30:[21, 20, 19, 17, 16, 15, 5, 4, 3, 1, -1, -11, -12, -13, -15, -16, -17],
					31:[21, 20, 17, 16, 5, 4, 1, -11, -12, -15, -16],
					32:[16, 15, 12, 11, -1, -4, -5, -16, -17, -20, -21],
					33:[17, 16, 15, 13, 12, 11, 1, -1, -3, -4, -5, -15, -16, -17, -19, -20, -21],
					34:[17, 16, 15, 13, 12, 11, 1, -1, -3, -4, -5, -15, -16, -17, -19, -20, -21],
					35:[17, 16, 13, 12, 1, -3, -4, -15, -16, -19, -20],
					36:[20, 19, 16, 15, 12, 11, 4, 3, -1, -4, -5, -12, -13, -16, -17, -20, -21],
					37:[21, 20, 19, 17, 16, 15, 13, 12, 11, 5, 4, 3, 1, -1, -3, -4, -5, -11, -12, -13, -15, -16, -17, -19, -20, -21],
					38:[21, 20, 19, 17, 16, 15, 13, 12, 11, 5, 4, 3, 1, -1, -3, -4, -5, -11, -12, -13, -15, -16, -17, -19, -20, -21],
					39:[21, 20, 17, 16, 13, 12, 5, 4, 1, -3, -4, -11, -12, -15, -16, -19, -20],
					40:[20, 19, 16, 15, 12, 11, 4, 3, -1, -4, -5, -12, -13, -16, -17, -20, -21],
					41:[21, 20, 19, 17, 16, 15, 13, 12, 11, 5, 4, 3, 1, -1, -3, -4, -5, -11, -12, -13, -15, -16, -17, -19, -20, -21],
					42:[21, 20, 19, 17, 16, 15, 13, 12, 11, 5, 4, 3, 1, -1, -3, -4, -5, -11, -12, -13, -15, -16, -17, -19, -20, -21],
					43:[21, 20, 17, 16, 13, 12, 5, 4, 1, -3, -4, -11, -12, -15, -16, -19, -20],
					44:[20, 19, 16, 15, 4, 3, -1, -12, -13, -16, -17],
					45:[21, 20, 19, 17, 16, 15, 5, 4, 3, 1, -1, -11, -12, -13, -15, -16, -17],
					46:[21, 20, 19, 17, 16, 15, 5, 4, 3, 1, -1, -11, -12, -13, -15, -16, -17],
					47:[21, 20, 17, 16, 5, 4, 1, -11, -12, -15, -16],
					48:[16, 15, 12, 11, -1, -4, -5],
					49:[17, 16, 15, 13, 12, 11, 1, -1, -3, -4, -5],
					50:[17, 16, 15, 13, 12, 11, 1, -1, -3, -4, -5],
					51:[17, 16, 13, 12, 1, -3, -4],
					52:[20, 19, 16, 15, 12, 11, 4, 3, -1, -4, -5],
					53:[21, 20, 19, 17, 16, 15, 13, 12, 11, 5, 4, 3, 1, -1, -3, -4, -5],
					54:[21, 20, 19, 17, 16, 15, 13, 12, 11, 5, 4, 3, 1, -1, -3, -4, -5],
					55:[21, 20, 17, 16, 13, 12, 5, 4, 1, -3, -4],
					56:[20, 19, 16, 15, 12, 11, 4, 3, -1, -4, -5],
					57:[21, 20, 19, 17, 16, 15, 13, 12, 11, 5, 4, 3, 1, -1, -3, -4, -5],
					58:[21, 20, 19, 17, 16, 15, 13, 12, 11, 5, 4, 3, 1, -1, -3, -4, -5],
					59:[21, 20, 17, 16, 13, 12, 5, 4, 1, -3, -4],
					60:[20, 19, 16, 15, 4, 3, -1],
					61:[21, 20, 19, 17, 16, 15, 5, 4, 3, 1, -1],
					62:[21, 20, 19, 17, 16, 15, 5, 4, 3, 1, -1],
					63:[21, 20, 17, 16, 5, 4, 1] }

def find_neighbors(board, position):
	neighbors = {}
	for offset in flat_dictionary[position]:
		index = position - offset
		neighbors[index] = board[index]
	return neighbors

def positions2word(board, positions):
	word = ''
	for p in positions:
		word += board[p]
	return word

def positions2voxels(positions):
	p2v = []
	for p in positions:
		p2v.append(voxels[p])
	return p2v

def find_word(board, word, position, index, walkabout):
	global walkabout_gl
	global speed
	walkabout.append(position)
	walkabout_voxels = positions2voxels(walkabout)
	lock.acquire()
	walkabout_gl = walkabout_voxels
	lock.release()
	time.sleep(speed/10)
	index += 1
	try:
		next_letter = word[index]
	except IndexError:
		return walkabout

	neighborhood = find_neighbors(board, position)
	for visited in walkabout:
		try:
			del neighborhood[visited]
		except:
			pass

	positions = [key for (key,value) in neighborhood.items() if value == next_letter]
	if positions:
		for position in positions:
			returned = find_word(board, word, position, index, walkabout)
			returned_voxels = positions2voxels(returned)
			lock.acquire()
			walkabout_gl = returned_voxels
			lock.release()
			returned_word = positions2word(board, returned)
			if returned_word == word:
				return returned
			walkabout.pop()

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
	for voxel in gl_voxels:
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
walkabout_gl = []
tCube = threading.Thread(target=render_gl, name='tCube')
tCube.start()
speed = 1

word_count = [0] * 1000
cube_index = 0

boggle_boards = [x.lower() for x in map(str.strip, cubes)]
# for board in random.sample(boggle_boards, 1):
## 951 is the index that has the most words (3340)
for board in [boggle_boards[951]]:
	cube = {k:v for k, v in zip(voxels, board)}
	tfl = []
	for letter in list(board):
		if letter not in tfl:
			tfl.append(letter)
		base_positions = [key for (key,value) in enumerate(board) if value == letter]
		for position in base_positions:
			neighborhood = find_neighbors(board, position)
			for neighbor in neighborhood:
				neighboring_letter = board[neighbor]
				if letter+neighboring_letter not in tfl:
					tfl.append(letter+neighboring_letter)

			
	for word in valid_words:
		if not tCube.is_alive():
			quit()
		if word[:2] in tfl:
			index = 0
			first_letter = word[index]
			base_positions = [key for (key,value) in enumerate(board) if value == first_letter]
			for position in base_positions:
				walkabout = []
				returned = find_word(board, word, position, index, walkabout)
				returned_voxels = positions2voxels(returned)
				lock.acquire()
				walkabout_gl = returned_voxels
				lock.release()
				returned_word = positions2word(board, returned)
				if returned_word == word:
					word_count[cube_index] += 1
					break

	print(word_count[cube_index])
	# cube_index += 1
