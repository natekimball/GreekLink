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
        return .3-.05*b
    if not b:
        return .34-.04*a
    return a1*math.log(b1+1)
        

def main():
    mat = [[round(f(a,b),3) for a in range(6)] for b in range(6)]
    print(*mat, sep='\n')
    
if __name__ == '__main__':
    main()