import sys

minScore = sys.float_info.max
minDenomination = [[0,0,0,0,0] for k in range(100)]
Denomination = [0,0,0,0,0]

def addArrays(arr1,arr2):
    return [ele + arr1[i] for i,ele in enumerate(arr2)]

""" Returns the Score for this denomination"""
def exactChange(denominations,N):
    score = 0.0
    global minScore
    global minDenomination
    global Denomination
    priceDenominations = [[0,0,0,0,0] for k in range(100)]
    for i in range(1,100):
        minPriceI = [100,100,100,100,100]
        coin = 0
        for k in range(0,5):
            if denominations[k] > i:
                break;
            if denominations[k] <= i and sum(minPriceI) >= sum(priceDenominations[i-denominations[k]]):
                minPriceI = priceDenominations[i-denominations[k]]
                coin = k
        priceDenominations[i][coin] += 1
        priceDenominations[i] = addArrays(priceDenominations[i],minPriceI)
        if (i%5==0):
            score += (N*sum(priceDenominations[i]))
        else:
            score += sum(priceDenominations[i])
        if score >= minScore:
            return
    if minScore > score:
        minScore = score
        minDenomination = priceDenominations
        Denomination = denominations
        
                                
if __name__ == "__main__":
    N = float(sys.argv[1])
    for i in range(5,6):
        for j in range(6,23):
            for k in range(18,43):
                for z in range(31,63):
                    exactChange([1,i,j,k,z],N)
    print "Score:" + str(minScore)
    print "Denominations:" + str(Denomination)
    for k in range(1,100):
        print str(k) + ":" + str(minDenomination[k])
                    
    
    
