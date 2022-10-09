#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
sys.stdout.reconfigure(line_buffering=True)

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

def find_word(board, word, position, index, walkabout):
	walkabout.append(position)
	index += 1
	try:
		next_letter = word[index]
	except IndexError:
		return walkabout

	neighborhood = find_neighbors(board, position)
	for visited in walkabout:
		if visited in neighborhood:
			del neighborhood[visited]

	positions = [key for (key,value) in neighborhood.items() if value == next_letter]
	if positions:
		for position in positions:
			returned = find_word(board, word, position, index, walkabout)
			returned_word = positions2word(board, returned)
			if returned_word == word:
				return returned
			walkabout.pop()

	return walkabout

word_count = [0] * 1000
cube_index = 0

boggle_boards = [x.lower() for x in map(str.strip, cubes)]
for board in boggle_boards:
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
		if word[:2] in tfl:
			index = 0
			first_letter = word[index]
			base_positions = [key for (key,value) in enumerate(board) if value == first_letter]
			for position in base_positions:
				walkabout = []
				returned = find_word(board, word, position, index, walkabout)
				returned_word = positions2word(board, returned)
				if returned_word == word:
					word_count[cube_index] += 1
					break

	print(word_count[cube_index])
	cube_index += 1

