import math
import heapq
from queue import Queue
import sys
from tabulate import tabulate

def main():
    [residGraph, littles, bigs, relationRanks, littleToNum, bigToNum] = input_handling()
    [edges, weightings] = weighting(relationRanks, littleToNum, bigToNum)
    # print(littles,bigs)
    # print(relationRanks)
    # print(weightings)
    print(littleToNum,bigToNum)
    print(weightings)
    # print(*residGraph, sep = "\n")
    result = weightedMaxFlow(residGraph, weightings, len(littles)+len(bigs)+1, edges)
    interpret(residGraph,littles, bigs)
    # print(edges)
    # print(weightings)
    # print(littles)
    # print(bigs)
    # print("flow", result)
    
def input_handling():
    if len(sys.argv) != 3:
        # filename = input("Enter filename consisting of little's rankings of bigs:\t")
        filename = "sampleinput/little_preferences.txt"
    else:
        filename = sys.argv[1]
    file = open(filename, "r")

    relationRanks = {}
    littles = []
    littleToNum = {}
    littlePrefs = {}
    little = file.readline().strip()
    x = 1
    while little != "":
        littles.append(little)
        littleToNum[little]=x
        littlePrefs[little] = []
        for i in range(5):
            [rank, big] = file.readline().strip().split(". ")
            relationRanks[(little, big)] = [int(rank),0]
            # relationRanks[(big, little)] = [int(rank),0]
            littlePrefs[little].append(big)
        file.readline()
        little = file.readline().strip()
        x +=1
        
    if len(sys.argv) != 3:
        # filename = input("Enter filename consisting of big's rankings of littles:\t")
        filename = "sampleinput/big_preferences.txt"
    else:
        filename = sys.argv[1]

    file = open(filename, "r")

    bigToNum = {}
    bigs = []
    bigPrefs = {}
    big = file.readline().strip()
    while big != "":
        bigs.append(big)
        bigToNum[big] = x
        bigPrefs[big] = []
        for i in range(5):
            [rank, little] = file.readline().strip().split(". ")
            if little not in littles:
                print("Error: " + little + " is not a little")
                exit()
            if (little,big) not in relationRanks:
                relationRanks[(little, big)] = [0,0]
                # relationRanks[(big, little)] = [0,0]
            relationRanks[(little, big)][1] = int(rank)
            # relationRanks[(big, little)][1] = int(rank)
            bigPrefs[big].append(little)
        file.readline()
        big = file.readline().strip()
        x+=1
    if len(littles) > len(bigs):
        n = math.ceil(len(littles)/len(bigs))
    else:
        n = math.ceil(len(bigs)/len(littles))
    # print("littles",littles)
    # print("littleToNum",littleToNum)
    # print("bigs",bigs)
    # print("bigToNum",bigToNum)
    # print("littlePrefs",littlePrefs)
    # print("bigPrefs",bigPrefs)
    # print("n",n)
    # print("relationRanks",relationRanks)
    # let n be the max cardinality of a matching
    residGraph = setUpResidGraph(littles, littleToNum, bigs, bigToNum, littlePrefs, bigPrefs, n, length=x+1)
    return [residGraph, littles, bigs, relationRanks, littleToNum, bigToNum]

def setUpResidGraph(littles, littleToNum, bigs, bigToNum, littlePrefs, bigPrefs, n, length):
    residGraph = [[0 for _ in range(length)] for _ in range(length)]
    for i in range(1,len(littles)+1):
        residGraph[0][i] = n
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
        path = edges.pop()
        path = [0, path[0], path[1], end]
        # path1 = djikstra(residGraph, relationRanks, end)
        # path2 = bfs(residGraph, relationRanks, end)
        # print(path)
        if not path:
            break
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
        print(q)
        (weight, node) = heapq.heappop(q)
        print("node: ",node, "weight:",weight)
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
    table = [[0, 0.3, 0.26, 0.22, 0.18, 0.14],
            [0.25, 0.693, 0.347, 0.231, 0.173, 0.139],
            [0.2, 0.405, 0.203, 0.135, 0.101, 0.081],
            [0.15, 0.288, 0.144, 0.096, 0.072, 0.058],
            [0.1, 0.223, 0.112, 0.074, 0.056, 0.045],
            [0.05, 0.182, 0.091, 0.061, 0.046, 0.036]]
    weightings = {}
    edges = [0]*len(relationRanks)
    i = 0
    for [a,b],rank in relationRanks.items():
        edges[i]=(littleToNum[a],bigToNum[b])
        weightings[(littleToNum[a],bigToNum[b])] = -table[rank[1]][rank[0]]
        i+=1
        # maybe make un negative?
    edges.sort(key = lambda x: weightings[x], reverse=True)
    return [edges, weightings]

def interpret(residGraph, littles, bigs):
    yourLittles = {}
    yourBigs = {}
    for i in range(len(littles)+1,len(residGraph)-1):
        for j in range(1,len(littles)+1):
            if residGraph[i][j] == 1:
                if bigs[i-len(littles)-1] not in yourBigs:
                    yourBigs[bigs[i-len(littles)-1]] = []
                yourBigs[bigs[i-len(littles)-1]].append(littles[j-1])
                if littles[j-1] not in yourLittles:
                    yourLittles[littles[j-1]] = []
                yourLittles[littles[j-1]].append(bigs[i-len(littles)-1])
                # print(littles[j-1] + " is matched with " + bigs[i-len(littles)-1])
    if len(bigs)>len(littles):
        print("LITTLES\t\t\t\tBIGS")
        for l,bs in yourBigs.items():
            print(l + "\t\t\t" + ", ".join(bs))
    else:
        print("BIG\t\t\t\tLITTLES")
        for b,ls in yourBigs.items():
            print(b + "\t\t\t" + ", ".join(ls))
    return [yourLittles, yourBigs]
    

if __name__ == '__main__':
    main()
# we could come up with a better solution to ranking the weightings
# perhaps give more weight if they both rank each other via multiplication or multiplying the logarithms of each rank
