import math
from ortools.sat.python import cp_model
import sys
# import time
from tabulate import tabulate

def big_little_match(littlefile, bigfile, bias):
    if bias:
        table = [[1, 10,  7,  5,  4,  2],
                [11, 36, 34, 30, 24, 21],
                [9, 35, 32, 26, 23, 18],
                [8, 33, 27, 25, 19, 15],
                [6, 31, 28, 20, 16, 13],
                [3, 29, 22, 17, 14, 12]]
    else:
        table = [[0,  5,  4,  3,  2,  1],
                [5, 21, 20, 18, 15, 10],
                [4, 20, 19, 17, 13,  9],
                [3, 18, 17, 14, 11,  8],
                [2, 15, 13, 11,  9,  7],
                [1, 10,  9,  8,  7,  6]]
    littles, bigs, x, solver, status, switched = algorithm(littlefile, bigfile, table)
    return big_little_interpret(littles, bigs, x, solver, status, switched)


def match(littlefile, bigfile):
    table = [[0,  5,  4,  3,  2,  1],
             [5, 21, 20, 18, 15, 10],
             [4, 20, 19, 17, 13,  9],
             [3, 18, 17, 14, 11,  8],
             [2, 15, 13, 11,  9,  7],
             [1, 10,  9,  8,  7,  6]]
    return custom_match(littlefile, bigfile, table)


def custom_match(littlefile, bigfile, table):
    littles, bigs, x, solver, status, _ = algorithm(littlefile, bigfile, table)
    return interpret(littles, bigs, x, solver, status)


def algorithm(littlefile, bigfile, table):
    [littles, bigs, relationRanks, n, switched] = handleinput(littlefile, bigfile)
    costGraph = setUpCostGraph(littles, bigs, relationRanks, table, switched)
    x, solver, status =  solve(littles, bigs, costGraph, n)
    return [littles, bigs, x, solver, status, switched]

def solve(littles, bigs, costGraph, n):
    model = cp_model.CpModel()
    x = {}
    for little in range(len(littles)):
        for big in range(len(bigs)):
            x[little, big] = model.NewBoolVar('x[%i,%i]' % (little, big))

    for little in range(len(littles)):
        model.Add(sum(x[little, big] for big in range(len(bigs))) <= n)
        model.Add(sum(x[little, big] for big in range(len(bigs))) > 0)
    for big in range(len(bigs)):
        model.AddExactlyOne([x[little, big] for little in range(len(littles))])
        model.Add(sum(x[little, big] for little in range(len(littles))) > 0)
    
    objective_terms = []
    for little in range(len(littles)):
        for big in range(len(bigs)):
            objective_terms.append(costGraph[little][big] * x[little, big])
    model.Minimize(sum(objective_terms))

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    
    return x, solver, status

class InvalidLittleException(Exception):
    pass

def handleinput(littlefile, bigfile):
    littleIterator = iter(littlefile)
    relationRanks = {}
    littles = []
    little = next(littleIterator).strip()
    while little != "":
        littles.append(little)
        while True:
            try:
                [rank, big] = next(littleIterator).strip().split(". ")
                relationRanks[(little, big)] = [int(rank), 0]
            except Exception:
                break
        try:
            little = next(littleIterator).strip()
        except StopIteration:
            break

    bigIterator = iter(bigfile)
    bigs = []
    big = next(bigIterator).strip()
    while big != "":
        bigs.append(big)
        while True:
            try:
                [rank, little] = next(bigIterator).strip().split(". ")
                if little not in littles:
                    raise InvalidLittleException("Error: " + little + " is not a little")
                if (little, big) not in relationRanks:
                    relationRanks[(little, big)] = [0, 0]
                relationRanks[(little, big)][1] = int(rank)
            except ValueError:
                break
            except StopIteration:
                break
        try:
            big = next(bigIterator).strip()
        except StopIteration:
            break
    
    switched = False
    if len(littles) > len(bigs):
        bigs, littles = littles, bigs
        switched = True
    n = math.ceil(len(bigs)/len(littles))
    return [littles, bigs, relationRanks, n, switched]

def setUpCostGraph(littles, bigs, relationRanks, table, switched):
    costGraph = [[0 for _ in range(len(bigs))] for _ in range(len(littles))]
    for l in range(len(littles)):
        for b in range(len(bigs)):
            little = littles[l]
            big = bigs[b]
            if switched:
                costGraph[l][b] = -table[relationRanks[(big, little)][0]][relationRanks[(
                    big, little)][1]] if (big, little) in relationRanks else 0
            else:
                costGraph[l][b] = -table[relationRanks[(little, big)][0]][relationRanks[(
                    little, big)][1]] if (little, big) in relationRanks else 0
    return costGraph

def big_little_interpret(littles, bigs, x, solver, status, switched):
    result = interpret(littles, bigs, x, solver, status)
    if switched:
        headers = ["BIGS", "LITTLES"]
    else:
        headers = ["LITTLES", "BIGS"]
    output = []
    for a, bs in result.items():
        output.append([a, ", ".join(bs)])
    return [headers, output]

class UnsolvableException(Exception):
    pass

def interpret(littles, bigs, x, solver, status):
    if status != cp_model.OPTIMAL and status != cp_model.FEASIBLE:
        raise UnsolvableException("Error: No solution found, double check your input")
    yourLittles = {}
    yourBigs = {}
    for little in range(len(littles)):
        for big in range(len(bigs)):
            if solver.BooleanValue(x[little, big]):
                if littles[little] not in yourBigs:
                    yourBigs[littles[little]]=[]
                yourBigs[littles[little]].append(bigs[big])
                if bigs[big] not in yourLittles:
                    yourLittles[bigs[big]]=[]
                yourLittles[bigs[big]].append(littles[little])
    # print("total cost:",solver.ObjectiveValue())
    return yourBigs

def readfile(filename):
    file = open(filename, "r")
    return file.readlines()

if __name__ == '__main__':
    # littlefilename = "resources/sampleinput/little_preferences.txt"
    littlefilename = "./resources/sampleinput/10littles.txt"
    # littlefilename = "resources/sampleinput/6bigs.txt"
    # littlefilename = "resources/sampleinput/l_hard.txt"
    # bigfilename = "resources/sampleinput/big_preferences.txt"
    bigfilename = "resources/sampleinput/6bigs.txt"
    # bigfilename = "resources/sampleinput/10littles.txt"
    # bigfilename = "resources/sampleinput/b_hard.txt"
    if "-l" in sys.argv:
        littlefilename = sys.argv[sys.argv.index("-l")+1]
    # else:
    #     littlefilename = input("Enter filename consisting of little's rankings of bigs:\t")
    if "-b" in sys.argv:
        bigfilename = sys.argv[sys.argv.index("-b")+1]
    # else:
    #     bigfilename = input("Enter filename consisting of big's rankings of littles:\t")
    littlefile = readfile(littlefilename)
    bigfile = readfile(bigfilename)
    # start = time.time()
    [headers, result] = big_little_match(littlefile, bigfile, True)
    # print("python took ", time.time() - start, "seconds")
    print(tabulate(result, headers=headers, tablefmt="grid"))