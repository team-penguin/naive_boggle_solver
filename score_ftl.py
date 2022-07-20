#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

cube_count = 1
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

cube_index = 0
boggle_boards = [x.lower() for x in map(str.strip, cubes[:cube_count])]

for b in boggle_boards:
    ftl = []
    letters = list(b)
    cube = {k:v for k, v in zip(voxels, letters)}
    for letter in letters:
        if letter not in ftl: ftl.append(letter)
        base_voxels = [key for (key, value) in cube.items() if value == letter]
        for voxel in base_voxels:
            neighborhood = find_neighbors(cube, voxel) 
            for neighbor in neighborhood:
                neighboring_letter = cube[neighbor]
                if letter+neighboring_letter not in ftl: ftl.append(letter+neighboring_letter)

    for valid_word in valid_words:
        if valid_word[:2] in ftl:
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
