from third_part.matlab_compat.matlab_native import num2str

def bmNumList(argNum):
    argNum -= 1
    numOfDigits = len(num2str(argNum))
    myString1 = num2str(10 ** numOfDigits)
    myLength1 = len(myString1)

    out = [None] * argNum
    for i in range(argNum + 1):
        myString2 = num2str(i)
        myLength2 = len(myString2)
        out[i] = myString1[:myLength1 - myLength2] + myString2

    return out
