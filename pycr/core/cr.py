import math, sys

class CR:
    def __init__(self, order, length):
        self.operands = [None for i in range(length)]
        self.order = order
    
    def __len__(self):
        return len(self.operands)
    
    def __getitem__(self, key):
        return self.operands[key]
    
    def __setitem__(self, key, value):
        self.operands[key] = value

    def __gt__(self, target):
        return self.order > target.order 
    
    def __lt__(self, target):
        return self.order < target.order
    
    def isnumber(self):
        return False
    
    def pop(self):
        return self.operands.pop()
    
    def copy(self):
        res = type(self)(self.order,self.length)
        for i in range(len(self)):
            res[i] = self[i].copy()
        return res
    
    def valueof(self):
        return self[0]
    
    def simplified(self):
        return self.copy()
    
class CRsum(CR):
    def simplified(self):
        result = self.copy()
        j = len(result) -1 
        while (j > 0) and isinstance(self[j], CRnum) and result[j].iszero():
            result.pop()
            j -= 1
        if j == 0:
            return CRnum(0)
        else:
            return result

class CRprod(CR):

    def simplified(self):
        result = self.copy()
        j = len(result) - 1
        while j > 0:
            if isinstance(result[j],CRnum) and result[j].iszero():
                while len(result) > j:
                    result.pop()
        if len(result) == 0:
            return CRnum(0)
        elif len(result) == len(self):
            j = len(result) - 1
            while j > 0 and isinstance(result[j],CRnum) and result[j].isone():
                result.pop()
                j -= 1
            if len(result) == 0:
                return CRnum(1)
            else:
                return result
    
    def correctP(self, newlength):
        result = CRprod(self.order, newlength)
        for i in range(len(self)):
            result[i] = self[i].copy()
        for i in range(len(self),newlength):
            result[i] = CRnum(1)
        return result

class CRnum(CR):
    def __init__(self, value):
        self.value = value
    
    def isnumber(self):
        return True
    
    def copy(self):
        return CRnum(self.value)
    
    def valueof(self):
        return self.value
    
    def iszero(self):
        return abs(self.value) < sys.float_info.epsilon
    
    def isone(self):
        return abs(self.value - 1) < sys.float_info.epsilon

class CRtrig(CR):
    
    def correctT(self, newlength):
        result = type(self)(self.order, newlength*2)
        for i in range(len(self)//2):
            result[i] = self[i].copy()
            result[i+newlength] = self[i+len(self)//2].copy()
        
        for i in range(len(self)//2, newlength):
            result[i] = CRnum(0)
            result[i+newlength] = CRnum(1)
        
        return result

    def simplified(self):
        t = len(self)//2
        if isinstance(self[0], CRnum) and self[0].iszero() and isinstance(self[t],CRnum) and self[t].iszero():
            return CRnum(0)
        return self.copy()


class CRsin(CRtrig):
    def valueof(self):
        return self[0]


class CRcos(CRtrig):
    def valueof(self):
        return self[len(self)//2]

class CRtan(CRtrig):
    def valueof(self):
        return self[0]/self[len(self)//2]


class CRcot(CRtrig):
    def valueof(self):
        return self[len(self)//2]/self[0]
    
# CRE is triggered when we have 

class CRE(CR):

    def __init__(self, operands):
        self.operands = operands
        order = -1
        for operand in operands:
            order = max(order, operand.order)

class CREadd(CR):

    def valueof(self):
        result = 0
        for i in range(len(self)):
            result += self[i].valueof()

class CREmul(CR):
    
    def valueof(self):
        result = 1
        for i in range(len(self)):
            result *= self[i].valueof()

class CREpow(CR):

    def valueof(self):
        return self[0] ** self[1]
    

    
            
        

