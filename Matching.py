import math
import heapq
from queue import Queue
import sys
from tabulate import tabulate

def match(littlefile, bigfile):
    [residGraph, littles, bigs, relationRanks, littleToNum, bigToNum] = input_handling(littlefile, bigfile)
    [edges, weightings] = weighting(relationRanks, littleToNum, bigToNum)
    # print(*residGraph, sep = "\n")
    flow = weightedMaxFlow(residGraph, weightings, len(littles)+len(bigs)+1, edges)
    [result, headers] = interpret(residGraph,littles, bigs, flow)
    return [result, headers]
    # print(littles,bigs)
    # print(edges)
    # print(relationRanks)
    # print(littleToNum,bigToNum)
    # print(weightings)
    # print("flow", flow)
    
def input_handling(littlefile, bigfile):
    relationRanks = {}
    littles = []
    littleToNum = {}
    littlePrefs = {}
    little = littlefile.readline().strip()
    x = 1
    while little != "":
        littles.append(little)
        littleToNum[little]=x
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
    
    bigToNum = {}
    bigs = []
    bigPrefs = {}
    big = bigfile.readline().strip()
    while big != "":
        bigs.append(big)
        bigToNum[big] = x
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
    # print("littleToNum",littleToNum)
    # print("bigs",bigs)
    # print("bigToNum",bigToNum)
    # print("littlePrefs",littlePrefs)
    # print("bigPrefs",bigPrefs)
    # print("n",n)
    # print("relationRanks",relationRanks)
    # let n/c be the max cardinality of a matching
    residGraph = setUpResidGraph(littles, littleToNum, bigs, bigToNum, littlePrefs, bigPrefs, n, m, length=x+1)
    return [residGraph, littles, bigs, relationRanks, littleToNum, bigToNum]

def setUpResidGraph(littles, littleToNum, bigs, bigToNum, littlePrefs, bigPrefs, n, m, length):
    residGraph = [[0 for _ in range(length)] for _ in range(length)]
    for i in range(1,len(littles)+1):
        residGraph[0][i] = m
    for i in range(len(littles)+1,length-1):
        residGraph[i][-1] = n
    # for little in littles:
    #     for big in littlePrefs[little]:
    #         residGraph[littleToNum[little]][bigToNum[big]] = 1
    # for big in bigs:
    #     for little in bigPrefs[big]:
    #         residGraph[littleToNum[little]][bigToNum[big]] = 1
    for i in range(1,len(littles)+1):
        for j in range(len(littles)+1,length-1):
            residGraph[i][j] = 1
    return residGraph

def weightedMaxFlow(residGraph, relationRanks, end, edges):
    maxFlow = 0
    # print(*residGraph, sep = "\n")
    while True:
        if not edges:
            break
        (u,v) = edges.pop()
        path = [0, u, v, end]
        # path1 = djikstra(residGraph, relationRanks, end)
        # path2 = bfs(residGraph, relationRanks, end)
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

def bfs(residGraph, relationRanks, end):
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

def weighting(relationRanks, littleToNum, bigToNum):
    table = [[ 1, 10,  7,  5,  4,  2],
             [11, 36, 34, 30, 24, 21],
             [ 9, 35, 32, 26, 23, 18],
             [ 8, 33, 27, 25, 19, 15],
             [ 6, 31, 28, 20, 16, 13],
             [ 3, 29, 22, 17, 14, 12]]
    # alt = [[0, 5, 4, 3, 2, 1],
    #        [5,16 15,13,10, 5],
    #        [4,15,14,12, 8, 4],
    #        [3,13, 12,9, 6, 3],
    #        [2,10, 8, 6, 4, 2],
    #        [1, 5, 4, 3, 2, 1]]
    weightings = {}
    edges = [0]*len(relationRanks)
    i = 0
    for [a,b],rank in relationRanks.items():
        # print([a,b],rank, -table[rank[0]][rank[1]])
        edges[i]=(littleToNum[a],bigToNum[b])
        weightings[(littleToNum[a],bigToNum[b])] = -table[rank[0]][rank[1]]
        i+=1
        # maybe make un negative?
    edges.sort(key = lambda x: weightings[x], reverse=True)
    return [edges, weightings]

def interpret(residGraph, littles, bigs, flow):
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
                # print(littles[j-1] + " is matched with " + bigs[i-len(littles)-1])
    if flow<max(len(littles),len(bigs)):
        print("No stable matching, some people are unmatched. Check your input files.")
    output = []
    if len(bigs)>len(littles):
        headers = ["LITTLES", "BIGS"]
        return [yourBigs, headers]
    else:
        headers=["BIGS","LITTLES"]
        return [yourLittles, headers]

if __name__ == '__main__':
    # littlefilename = "sampleinput/little_preferences.txt"
    littlefilename = "sampleinput/10littles.txt"
    # littlefilename = "sampleinput/6bigs.txt"
    # bigfilename = "sampleinput/big_preferences.txt"
    bigfilename = "sampleinput/6bigs.txt"
    # bigfilename = "sampleinput/10littles.txt"
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
    [result, headers] = match(littlefile, bigfile)
    output = []
    for a,bs in result.items():
        output.append([a,", ".join(bs)])
    print(tabulate(output, headers=headers, tablefmt="grid"))