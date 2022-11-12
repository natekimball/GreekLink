import math

def f(a,b):
    if a:
        a1 = 1/a
    else:
        a1 = 0
    if b:
        b1 = 1/b
    else:
        b1 = 0
    c = 0
    if not a and not b:
        return 0
    if not a:
        return .38-.04*b
    if not b:
        return .35-.05*a
    return a1*math.log(b1+1) 

def main():
    # mat = [[round(f(a,b),3) for a in range(6)] for b in range(6)]
    # print(*mat, sep='\n')
    table = [[0, 0.3, 0.25, 0.2, 0.15, 0.1],
            [0.34, 0.693, 0.347, 0.201, 0.115, 0.081],
            [0.3, 0.405, 0.231, 0.135, 0.095, 0.069],
            [0.26, 0.288, 0.144, 0.123, 0.074, 0.05],
            [0.22, 0.223, 0.150, 0.080, 0.056, 0.045],
            [0.05, 0.182, 0.091, 0.061, 0.046, 0.036]]
    x = 0
    for _ in range(6):
        for _ in range(6):
            m = min(table)
            for i,row in enumerate(table):
                for j,column in enumerate(row):
                    if column == m:
                        y = (i,j)
                        break
                        x+=1
                        table[i][j] = 1
    
if __name__ == '__main__':
    main()