import math
import heapq
from queue import Queue
import sys
from tabulate import tabulate

def main():
    # input_handling()
    [residGraph, littles, bigs, relationRanks, littleToNum, bigToNum] = input_handling()
    end = len(littles)+len(bigs)+1
    [edges, weightings] = weighting(relationRanks, littles, bigs, littleToNum, bigToNum)
    print(edges)
    print(weightings)
    result = weightedMaxFlow(residGraph, weightings, end, edges)
    print(*residGraph, sep = "\n")
    print(littles)
    print(bigs)
    print("flow", result)
    interpret(residGraph,littles, bigs)
    
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
    for little in littles:
        for big in littlePrefs[little]:
            residGraph[littleToNum[little]][bigToNum[big]] = 1
    return residGraph

def weightedMaxFlow(residGraph, relationRanks, end, edges):
    maxFlow = 0
    print(*residGraph, sep = "\n")
    while True:
        if not edges:
            break
        path = edges.pop()
        path = [0, path[0], path[1], end]
        path1 = djikstra(residGraph, relationRanks, end)
        path2 = bfs(residGraph, relationRanks, end)
        if not path:
            break
        print(path)
        if not all([residGraph[path[i]][path[i+1]] for i in range(len(path)-1)]):
            continue
        for i in range(len(path)-1):
            residGraph[path[i]][path[i+1]] -= 1
            residGraph[path[i+1]][path[i]] += 1
        maxFlow += 1
        print(*residGraph, sep = "\n")
    return maxFlow

def djikstra(residGraph, weightings, end):
    q = [(0,0)]
    visited = [False]*len(residGraph)
    visited[0] = True
    parents = [-1]*len(residGraph)
    while q:
        # print(q)
        (weight, node) = heapq.heappop(q)
        # print("node: ",node, "weight:",weight)
        if node == len(residGraph)-1:
            break
        for i, val in enumerate(residGraph[node]):
            if val<=0 or i<=node:
                continue
            if i == 0 or i == end or node == 0 or node == end:
                weight = 0
            elif i > node:
                weight += weightings[(node,i)]
            else:
                weight += weightings[(i,node)]
            if not visited[i]:
                visited[i] = True
                heapq.heappush(q, (weight, i))
                parents[i] = node
            else:
                for j in range(len(q)):
                    if q[j][1] == i:
                        if weight > q[j][0]:
                            q[j] = (weight, i)
                            parents[i] = node
                            heapq.heapify(q)
                        break
        # print(q)
    if parents[-1] == -1:
        return None
    path = [len(residGraph)-1]
    while path[-1]:
        path.append(parents[path[-1]])
    return path[::-1]

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

def weighting(relationRanks, littles, bigs, littleToNum, bigToNum):
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
