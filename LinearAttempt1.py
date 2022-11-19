from ortools.sat.python import cp_model
import sys
import time
from tabulate import tabulate
import numpy as np
from scipy.optimize import linear_sum_assignment


def big_little_match(littlefile, bigfile):
    table = [[1, 10,  7,  5,  4,  2],
             [11, 36, 34, 30, 24, 21],
             [9, 35, 32, 26, 23, 18],
             [8, 33, 27, 25, 19, 15],
             [6, 31, 28, 20, 16, 13],
             [3, 29, 22, 17, 14, 12]]
    [row_ind, col_ind, littles, bigs] = algorithm(littlefile, bigfile, table)
    return big_little_interpret(row_ind, col_ind, littles, bigs)


def match(littlefile, bigfile):
    table = [[0,  5,  4,  3,  2,  1],
             [5, 21, 20, 18, 15, 10],
             [4, 20, 19, 17, 13,  9],
             [3, 18, 17, 14, 11,  8],
             [2, 15, 13, 11,  9,  7],
             [1, 10,  9,  8,  7,  6]]
    [row_ind, col_ind, littles, bigs] = algorithm(littlefile, bigfile, table)
    return interpret(row_ind, col_ind, littles, bigs)


def match(littlefile, bigfile, table):
    [row_ind, col_ind, littles, bigs] = algorithm(littlefile, bigfile, table)
    return interpret(row_ind, col_ind, littles, bigs)


def algorithm(littlefile, bigfile, table):
    [littles, bigs, relationRanks] = handleinput(littlefile, bigfile)
    costGraph = setUpCostGraph(littles, bigs, relationRanks, table)
    costGraph = np.array(costGraph)
    row_ind, col_ind = linear_sum_assignment(costGraph, maximize=True)
    print("Total cost: ", costGraph[row_ind, col_ind].sum())
    return [row_ind, col_ind, littles, bigs]


def handleinput(littlefile, bigfile):
    relationRanks = {}
    littles = []
    little = littlefile.readline().strip()
    x = 0
    while little != "":
        littles.append(little)
        for _ in range(5):
            [rank, big] = littlefile.readline().strip().split(". ")
            relationRanks[(little, big)] = [int(rank), 0]
        littlefile.readline()
        little = littlefile.readline().strip()
    littlefile.close()

    bigs = []
    big = bigfile.readline().strip()
    while big != "":
        bigs.append(big)
        for _ in range(5):
            [rank, little] = bigfile.readline().strip().split(". ")
            if little not in littles:
                print("Error: " + little + " is not a little")
                exit()
            if (little, big) not in relationRanks:
                relationRanks[(little, big)] = [0, 0]
            relationRanks[(little, big)][1] = int(rank)
        bigfile.readline()
        big = bigfile.readline().strip()
    bigfile.close()
    return [littles, bigs, relationRanks]

# def setUpCostGraph1(littles, bigs, relationRanks, table):
#     length = max(len(littles), len(bigs))
#     costGraph = [[0 for _ in range(length)] for _ in range(length)]
#     # costGraph = np.zeros(len(littles), len(bigs))
#     for i in range(length):
#         for j in range(length):
#             if i>=len(littles) and j>=len(bigs):
#                 continue
#             if i<len(littles) and j<len(bigs):
#                 continue
#             little = littles[min(i,j)]
#             big = bigs[max(i,j)%len(bigs)]
#             costGraph[i][j] = -table[relationRanks[(little,big)][0]][relationRanks[(little,big)][1]] if (little,big) in relationRanks else 0
#     return costGraph


def setUpCostGraph(littles, bigs, relationRanks, table):
    length = max(len(littles), len(bigs))
    costGraph = [[0 for _ in range(length)] for _ in range(length)]
    # costGraph = np.zeros(len(littles), len(bigs))
    for i in range(length):
        for j in range(length):
            little = littles[i % len(littles)]
            big = bigs[j % len(bigs)]
            costGraph[i][j] = table[relationRanks[(little, big)][0]][relationRanks[(
                little, big)][1]] if (little, big) in relationRanks else 0
    return costGraph


def big_little_interpret(row_ind, col_ind, littles, bigs):
    result = interpret(row_ind, col_ind, littles, bigs)
    if len(bigs) > len(littles):
        headers = ["LITTLES", "BIGS"]
    else:
        headers = ["BIGS", "LITTLES"]
    output = []
    for a, bs in result.items():
        output.append([a, ", ".join(bs)])
    return [headers, output]


def interpret(row_ind, col_ind, littles, bigs):
    yourLittles = {}
    yourBigs = {}
    for i in range(len(row_ind)):
        big = bigs[col_ind[i] % len(bigs)]
        little = littles[row_ind[i] % len(littles)]
        if little not in yourBigs:
            yourBigs[little] = []
        yourBigs[little].append(big)
        if big not in yourLittles:
            yourLittles[big] = []
        yourLittles[big].append(little)
    if len(bigs) > len(littles):
        return yourBigs
    return yourLittles


if __name__ == '__main__':
    # littlefilename = "resources/sampleinput/little_preferences.txt"
    littlefilename = "./resources/sampleinput/10littles.txt"
    # littlefilename = "resources/sampleinput/6bigs.txt"
    # bigfilename = "resources/sampleinput/big_preferences.txt"
    bigfilename = "resources/sampleinput/6bigs.txt"
    # bigfilename = "resources/sampleinput/10littles.txt"
    if "-l" in sys.argv:
        littlefilename = sys.argv[sys.argv.index("-l")+1]
    # else:
    #     littlefilename = input("Enter filename consisting of little's rankings of bigs:\t")
    if "-b" in sys.argv:
        bigfilename = sys.argv[sys.argv.index("-b")+1]
    # else:
    #     bigfilename = input("Enter filename consisting of big's rankings of littles:\t")
    littlefile = open(littlefilename, "r")
    bigfile = open(bigfilename, "r")
    # start = time.time()
    [headers, result] = big_little_match(littlefile, bigfile)
    # print("python took ", time.time() - start, "seconds")
    print(tabulate(result, headers=headers, tablefmt="grid"))