#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

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
			# neighboring_cubies.update({ n : None })
			neighboring_cubies[n] = None
	for x in list(neighboring_cubies):
		if neighboring_cubies[x] is None:
			del neighboring_cubies[x]
	return neighboring_cubies

def arr2word(cube, voxels):
	word = ""
	for v in voxels:
		word += cube[v]
	return word

def find_voxels(cube, word, index, valid_word, voxel, walkabout):
	walkabout.append(voxel)
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
			returned_word = arr2word(cube, returned)
			if returned_word == valid_word:
				return returned
			walkabout.pop()
	index -= 1
	return walkabout

## A list of strings is totally inappropriate, use [RG] tuples.
# voxels = [ '0,0,0','0,1,0','0,2,0','0,3,0','1,0,0','1,1,0','1,2,0','1,3,0','2,0,0','2,1,0','2,2,0','2,3,0','3,0,0','3,1,0','3,2,0','3,3,0',
#            '0,0,1','0,1,1','0,2,1','0,3,1','1,0,1','1,1,1','1,2,1','1,3,1','2,0,1','2,1,1','2,2,1','2,3,1','3,0,1','3,1,1','3,2,1','3,3,1',
#            '0,0,2','0,1,2','0,2,2','0,3,2','1,0,2','1,1,2','1,2,2','1,3,2','2,0,2','2,1,2','2,2,2','2,3,2','3,0,2','3,1,2','3,2,2','3,3,2',
#            '0,0,3','0,1,3','0,2,3','0,3,3','1,0,3','1,1,3','1,2,3','1,3,3','2,0,3','2,1,3','2,2,3','2,3,3','3,0,3','3,1,3','3,2,3','3,3,3' ]

# [RG] List comprehension works nicely here.                                                
voxels = [ (i,j,k) for i in range(4) for j in range(4) for k in range(4)]

word_count = [0] * 1000
cube_index = 0

# [RG] This is the recommended way to open files: no explicit "close" call necessary.
with open("./cubes.txt",'r') as cube_file:                                          
	cubes = cube_file.readlines()
# [RG] Single line list comprehension instead of iteration.                          
boggle_boards = [x.lower() for x in map(str.strip, cubes[:RG_CUBE_COUNT])]
for b in boggle_boards:
	letters =  list(b)
	cube = {k:v for k, v in zip(voxels, letters)}
	for valid_word in valid_words:
		array_word = list(valid_word)
		index = 0
		first_letter = array_word[index]
		base_voxels = [key for (key, value) in cube.items() if value == first_letter]
		for voxel in base_voxels:
			walkabout = []
			returned = find_voxels(cube, array_word, index, valid_word, voxel, walkabout)
			returned_word = arr2word(cube, returned)
			if returned_word == valid_word:
				word_count[cube_index] += 1
				break

	print(word_count[cube_index])
	cube_index += 1
