import math
import heapq
from queue import Queue
import sys
import time
from tabulate import tabulate

def match(littlefile, bigfile):
    table = [[0,  5,  4,  3,  2,  1],
             [5, 21, 20, 18, 15, 10],
             [4, 20, 19, 17, 13,  9],
             [3, 18, 17, 14, 11,  8],
             [2, 15, 13, 11,  9,  7],
             [1, 10,  9,  8,  7,  6]]
    # decrease weight of 0s
    residGraph, littles, bigs, flow = algorithm(littlefile, bigfile, table)
    return interpret(residGraph,littles, bigs, flow)

def big_little_match(littlefile, bigfile):
    table = [[ 1, 10,  7,  5,  4,  2],
             [11, 36, 34, 30, 24, 21],
             [ 9, 35, 32, 26, 23, 18],
             [ 8, 33, 27, 25, 19, 15],
             [ 6, 31, 28, 20, 16, 13],
             [ 3, 29, 22, 17, 14, 12]]
    residGraph, littles, bigs, flow = algorithm(littlefile, bigfile, table)
    return big_little_interpret(residGraph, littles, bigs, flow)

def custom_match(littlefile, bigfile, table):
    [residGraph, littles, bigs, flow] = algorithm(littlefile, bigfile, table)
    return interpret(residGraph,littles, bigs, flow)

def algorithm(littlefile, bigfile, table):
    [residGraph, littles, bigs, relationRanks, indexes, indexes] = input_handling(littlefile, bigfile)
    [edges, weightings] = weighting(relationRanks, indexes, table)
    flow = weightedMaxFlow(residGraph, weightings, len(littles)+len(bigs)+1, edges)
    # print(*residGraph, sep = "\n")
    # print(weightings)
    return residGraph,littles,bigs,flow
    # print(littles,bigs)
    # print(edges)
    # print(relationRanks)
    # print(indexes,indexes)
    # print("flow", flow)
    
def input_handling(littlefile, bigfile):
    relationRanks = {}
    littles = []
    indexes = {}
    littlePrefs = {} # not needed
    little = littlefile.readline().strip()
    x = 1
    while little != "":
        littles.append(little)
        indexes[little]=x
        littlePrefs[little] = []
        for i in range(5):
            [rank, big] = littlefile.readline().strip().split(". ")
            relationRanks[(little, big)] = [int(rank),0]
            # relationRanks[(big, little)] = [int(rank),0]
            littlePrefs[little].append(big)
        littlefile.readline()
        little = littlefile.readline().strip()
        x +=1
    littlefile.close()
    
    bigs = []
    bigPrefs = {}
    big = bigfile.readline().strip()
    while big != "":
        bigs.append(big)
        indexes[big] = x
        bigPrefs[big] = []
        for i in range(5):
            [rank, little] = bigfile.readline().strip().split(". ")
            if little not in littles:
                print("Error: " + little + " is not a little")
                exit()
            if (little,big) not in relationRanks:
                relationRanks[(little, big)] = [0,0]
                # relationRanks[(big, little)] = [0,0]
            relationRanks[(little, big)][1] = int(rank)
            # relationRanks[(big, little)][1] = int(rank)
            bigPrefs[big].append(little)
        bigfile.readline()
        big = bigfile.readline().strip()
        x+=1
    if len(littles) > len(bigs):
        n = math.ceil(len(littles)/len(bigs))
        m = 1
    else:
        n = 1
        m = math.ceil(len(bigs)/len(littles))
    bigfile.close()
    # print("littles",littles)
    # print("indexes",indexes)
    # print("bigs",bigs)
    # print("indexes",indexes)
    # print("littlePrefs",littlePrefs)
    # print("bigPrefs",bigPrefs)
    # print("n",n)
    # print("relationRanks",relationRanks)
    # let n/c be the max cardinality of a matching
    residGraph = setUpResidGraph(len(littles)+1, n, m, length=x+1)
    return [residGraph, littles, bigs, relationRanks, indexes, indexes]

def setUpResidGraph(l, n, m, length):
    residGraph = [[0 for _ in range(length)] for _ in range(length)]
    for i in range(1,l+1):
        residGraph[0][i] = m
    for i in range(l,length-1):
        residGraph[i][-1] = n
    for i in range(1,l):
        for j in range(l,length-1):
            residGraph[i][j] = 1
    return residGraph

def weighting(relationRanks, indexes, weights_table):
    weightings = {}
    edges = [0]*len(relationRanks)
    i = 0
    for [a,b],rank in relationRanks.items():
        # print([a,b],rank, -table[rank[0]][rank[1]])
        edges[i]=(indexes[a],indexes[b])
        weightings[(indexes[a],indexes[b])] = -weights_table[rank[0]][rank[1]]
        i+=1
        # maybe make un negative?
    edges.sort(key = lambda x: weightings[x], reverse=True)
    return [edges, weightings]

def weightedMaxFlow(residGraph, relationRanks, end, edges):
    maxFlow = 0
    # print(*residGraph, sep = "\n")
    while True:
        if not edges:
            break
        (u,v) = edges.pop()
        path = [0, u, v, end]
        # path1 = djikstra(residGraph, relationRanks, end)
        # print(path)
        # if not path:
        #     break
        if not all([residGraph[path[i]][path[i+1]] for i in range(len(path)-1)]):
            continue
        for i in range(len(path)-1):
            residGraph[path[i]][path[i+1]] -= 1
            residGraph[path[i+1]][path[i]] += 1
        maxFlow += 1
        # print(*residGraph, sep = "\n")
    return maxFlow

def djikstra(residGraph, weightings, end):
    q = [(0,0)]
    visited = [False]*len(residGraph)
    visited[0] = True
    parents = [-1]*len(residGraph)
    dist = [0]*len(residGraph)
    while q:
        # print(q)
        (weight, node) = heapq.heappop(q)
        # print("node: ",node, "weight:",weight)
        if node == len(residGraph)-1:
            break
        for i, val in enumerate(residGraph[node]):
            if val<=0:
                continue
            weight = dist[node]
            if (node, i) in weightings:
                weight += weightings[(node,i)]
            if not visited[i]:
                dist[i] = weight
                visited[i] = True
                heapq.heappush(q, (dist[i], i))
                parents[i] = node
            elif dist[i] > weight:
                dist[i] = weight
                parents[i] = node
                decreaseKey(q, weight, i)
    if parents[-1] == -1:
        return None
    path = [len(residGraph)-1]
    while path[-1]:
        path.append(parents[path[-1]])
    return path[::-1]

def decreaseKey(q, weight, i):
    for j in q:
        if j[1] == i:
            j = (weight, i)
            heapq.heapify(q)
            break

def bfs(residGraph, end):
    q = Queue()
    q.put(0)
    visited = [False]*len(residGraph)
    visited[0] = True
    parents = [-1]*len(residGraph)
    while not q.empty():
        node = q.get()
        if node == end:
            break
        for i, val in enumerate(residGraph[node]):
            if val > 0 and not visited[i]:
                visited[i] = True
                q.put(i)
                parents[i] = node
    if parents[-1] == -1:
        return None
    path = [len(residGraph)-1]
    while path[-1]:
        path.append(parents[path[-1]])
    return path[::-1]

def interpret(residGraph, littles, bigs, flow):
    if flow<max(len(littles),len(bigs)):
        print("No stable matching, some people are unmatched. Check your input files.")
    yourLittles = {}
    yourBigs = {}
    for i in range(len(littles)+1,len(residGraph)-1):
        for j in range(1,len(littles)+1):
            if residGraph[i][j] == 1:
                if bigs[i-len(littles)-1] not in yourLittles:
                    yourLittles[bigs[i-len(littles)-1]] = []
                yourLittles[bigs[i-len(littles)-1]].append(littles[j-1])
                if littles[j-1] not in yourBigs:
                    yourBigs[littles[j-1]] = []
                yourBigs[littles[j-1]].append(bigs[i-len(littles)-1])
    if len(bigs)>len(littles):
        return yourBigs
    return yourLittles
    
def big_little_interpret(residGraph, littles, bigs, flow):
    result = interpret(residGraph, littles, bigs, flow)
    if len(bigs)>len(littles):
        headers = ["LITTLES", "BIGS"]
    else:
        headers = ["BIGS","LITTLES"]
    output = []
    for a,bs in result.items():
        output.append([a,", ".join(bs)])
    return [headers, output]

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

