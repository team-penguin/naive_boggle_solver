#!/usr/bin/env python3
# -*- coding: utf-8 -*-

## Imagine that you have a 4x4x4 cube of letters, with each of the 64 "cubies" containing a single letter.
## The "cube" source is represented by a 64 character string of letters.
## The 1st problem is representing this 64 character string as a 3D object from which neighboring "cubies" can be extracted.
## Fast-forward to another notion... What if the neighboring "cubies" can be extracted from the 64 character string directly.
## This script performs the following:
##
##    1) Create a 3D object from a 64 character string of letters.
##    2) Iterate over the 64 character string and calculate the neighboring "cubie" coordinates.
##    3) Convert the 3D coordinates from the "neighborhood" into indexes that address the 64 character string.
##    4) Iterate over the 1D "neighborhood" and calculate offsets relative to the sample position.
##    5) Create a dictionary of the discovered offsets with the sample positions as values.
##
## The 'flat_dictionary' variable is the the list of offsets for each element in a list of 64 characters.

import re
import pprint
import collections

with open("./cubes.txt",'r') as cube_file:
	cubes = cube_file.readlines()

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

boggle_boards = [x.lower() for x in map(str.strip, cubes)]
voxels = [(i,j,k) for i in range(4) for j in range(4) for k in range(4)]

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

for board in boggle_boards[:1]:
	voxel_letters = list(board)
	cube = {k:v for k,v in zip(voxels, voxel_letters)}
	offset_positions = {}
	for word in valid_words:
		index = 0
		first_letter = word[index]
		base_voxels = [key for (key, value) in cube.items() if value == first_letter]
		flat_voxels = []
		for voxel in base_voxels:
			## Answer #4: https://stackoverflow.com/questions/7367770/how-to-flatten-or-index-3d-array-in-1d-array
			#  Flat[ x * height * depth + y * depth + z ] = elements[x][y][z] where [WIDTH][HEIGHT][DEPTH]
			flat_voxel = (voxel[0] * 4 * 4) + (voxel[1] * 4) + voxel[2]
			flat_voxels.append(flat_voxel)
			neighborhood = find_neighbors(cube, voxel)
			sorted_neighborhood = {}
			for n in neighborhood:
				i = voxels.index(n)
				sorted_neighborhood[i] = cube[(n)]
			od_sorted_neighborhood = collections.OrderedDict(sorted(sorted_neighborhood.items()))
			offsets = []
			for od in od_sorted_neighborhood:
				offsets.append(flat_voxel - od)
			try:
				offset_positions[tuple(offsets)].append(flat_voxel)
			except KeyError:
				offset_positions[tuple(offsets)] = [flat_voxel]

	for k,v in {**offset_positions, **offset_positions}.items():
		print(k, ' => ', sorted(set(v)))
	print()
	pp = pprint.PrettyPrinter(width=120, compact=True)
	pp.pprint(flat_dictionary)
