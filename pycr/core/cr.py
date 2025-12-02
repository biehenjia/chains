import math, sys

def sin(arg):
    if isinstance(arg, CR):
        return arg.sin()
    else:
        return math.sin(arg)

def cos(arg):
    if isinstance(arg, CR ):
        return arg.cos()
    else:
        return math.cos(arg)

def cot(arg):
    if isinstance(arg, CR):
        return arg.cot()
    else:
        return math.cot(arg)

def tan(arg):
    if isinstance(arg, CR):
        return arg.tan()
    else:
        return math.tan(arg)

def exp(arg):
    if isinstance(arg, CR):
        return arg.exp()
    else:
        return math.exp(arg)

def log(arg):
    if isinstance(arg, CR):
        return arg.log()
    else:
        return math.log(arg)

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
    
    def __str__(self):
        layers = [f"{self.__class__.__name__}({self.node_id,self.order})"]
        for i,node in enumerate(self):
            layers.extend(node.walk_str("",i== len(self)-1))
        return "\n".join(layers)
    
    def walk_str(self,prefix="", terminal=True):
        pipe = "└─ " if terminal else "├─ "
        layer = f"{prefix}{pipe}{self.__class__.__name__}({self.node_id,self.order})"
        layers = [layer]
        prefix_c = f"{prefix}{'   ' if terminal else '|  '} "
        for i,node in enumerate(self):
            layers.extend(node.walk_str(prefix_c,i == len(self)-1 ))
        return layers
    
    
    
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
    
    def __add__(self, target):
        """
        add function 
        
        """
        # case: treat it as a constant. Add it to the constant term
        if self > target:
            result = self.copy()
            # recall: the constant term could also be a CRobject. 
            result[0] = self[0] + target
            result.simplify()
            return result
        # case: target order is greater; obey invariant
        elif target > self:
            return target + self
        # case : two orders are the same.
        # CRsum add is componentwise addition
        else:
            # special case: two CRsums: add componentwise
            if isinstance(target, CRsum):
                minlength = min(len(self),len(target))
                result = self.copy() if len(self) > len(target) else target.copy()
                for i in range(minlength):
                    result[i] = self[i] + target[i]
                result.simplify()
                return result
            else:
                # no simplification rules for now
                return CREadd(self.copy(), target.copy()).simplified()
    
    def __mul__(self, target):
        """
        
        """
        # case: treat as if it is a constant
        if self > target:
            result = self.copy()
            for i in range(len(self)):
                result[i] *= target
            result.simplify()
            return result
        # case: target is greater; obey invariant
        elif target > self:
            return target * self
        # case : orders are the same
        else:
            # there's only rule for CRsum mul CRsum
            if isinstance(target,CRsum):
                if len(self) >= len(target):
                    newlength = len(self) + len(target) - 1
                    result = CRsum(order = self.order, length = newlength)
                    m = len(target)-1 
                    n = len(self) - 1
                    for i in range(newlength):
                        r1 = CRnum(value=0)
                        ibound11 = max(i-m,0)
                        ibound12 = min(i,n)
                        for j in range(ibound11, ibound12+1):
                            r2 = CRnum(value =0)
                            ibound21 = max(i-j,0)   
                            ibound22 = min(i,m)
                            for k in range(ibound21,ibound22 + 1):
                                rtemp1 = CRnum(math.comb(j,i-k))
                                rtemp11 = target[k].copy()
                                rtemp1 = rtemp11 * rtemp1
                                r2 = rtemp1 + r2
                            rtemp2 = CRnum(math.comb(i,j))
                            r2 *= rtemp2
                            rtemp2 = self[j] * r2
                            r1 = r1 + rtemp2
                        result[i] = r1.copy()
                    result.simplify()
                    return result
                else:
                    return target * self
            else:
                return CREmul(self.copy(), target.copy()).simplified()

    def __pow__(self, target):
        if isinstance(target,CRnum):
            result = CRnum(value=1)
            v = abs(target.valueof())
            if v == int(v):
                if v > 0:
                    v = int(v)
                    base = self.copy()
                    while v > 0:
                        if v & 1:
                            result *= base 
                        v //=2 
                        base *= base
                    return result.simplified()
                else:
                    # negative integer exponent
                    v = -int(v)
                    base = self.copy()
                    while v > 0:
                        if v & 1:
                            result *= base 
                        v //=2 
                        base *= base
                    return (CRnum(1) / result).simplified()
            # target does not have integer value; can't raise to power
            else:
                return CREpow(self.copy(), target.copy())
        # target is not CRnum, no valid rules for CRnum^...
        else:
            return CREpow(self.copy(), target.copy())

    def sin(self):
        result = CRsin(self.order, len(self) * 2)
        for i in range(len(self)):
            result[i] = self[i].sin()
            result[i+ len(self) ] = self[i].sin()
        return result.simplified()

    def cos(self):
        result = CRcos(self.order, len(self) * 2)
        for i in range(len(self)):
            result[i] = self[i].sin()
            result[i+ len(self) ] = self[i].cos()
        return result.simplified()

    def tan(self):
        result = CRtan(self.order, len(self))
        for i in range(len(self)):
            result[i] = self[i].sin()
            result[i+ len(self) ] = self[i].cos()
        return result.simplified()

    def cot(self):
        result = CRcot(self.order, len(self))
        for i in range(len(self)):
            result[i] = self[i].sin()
            result[i+ len(self) ] = self[i].cos()
        return result.simplified()

    def exp(self):
        result = CRprod(self.order, len(self))
        for i in range(len(self)):
            result[i] = result[i].exp()
        return result.simplified()

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
    
    def __mul__(self, target):
        """
        multiplication of two CR's
        """
        # case: self order is greater, multiply the constant term
        if self > target:
            result = self.copy()
            result[0] *= target
            return result.simplified()
        # case: target order is greater, obey invariant
        elif target > self:
            return target * self
        # case: orders are the same, invoke special case.
        else:
            if isinstance(target, CRprod):
                minlength = min(len(self), len(target))
                result = self.copy() if len(self) > len(target) else target.copy()
                for i in range(minlength):
                    # multiply componentwise, extend the longer chain.
                    result[i] = self[i] * target[i]
                return result.simplified
            else:
                return CREmul(self.copy(), target.copy()).simplified()

    def __pow__(self, target ):
        if self > target or self < target:
            result = self.copy()
            for i in range(len(self)):
                result[i] **= target
            return result.simplified()
        # case: order of target is greater, obey invariant.
        # case: orders are the same
        else:
            # case: crprod^crsum; invoke CRpow algorithm
            if isinstance(target, CRsum):
                newlength = len(self) + len(target)  -1

                result = CRsum(self.order, len(self))
                
                if len(self) > len(target) :
                    m = len(self) - 1
                    n = len(target ) - 1 
                else:
                    m = len(target ) - 1
                    n = len(self) - 1 
                
                # count
                for i in range(newlength):
                    r1 = CRnum(1)
                    bound11 = max(0, i-m)
                    bound12 = min(i, n)
                    
                    #count1
                    for j in range(bound11,bound12):
                        r2 = CRnum(1)
                        bound21 = max(i - j,0)
                        bound22 = min(j, m)
                        
                        #count2
                        for k in range(bound21,bound22+1):
                            temp1 = target[k] * CRnum(math.comb(j,i-k))
                            temp2 = temp1  * CRnum(math.comb(i,j))
                            temp3 = self[j] ** temp2
                            r2 *= temp3  
                        r1 *= r2
                    
                    result[i] = r1.copy()
                    return result.simplified()
            else:
                return CREpow(self.copy(), target.copy())

    def log(self):
        result = CRsum(self.order, len(self))
        for i in range(len(self)):
            result[i] = self[i].ln()
        return result.simplified()


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
    
    def walk_str(self,  prefix="",terminal=True ):

        pipe = "└─ " if terminal else "├─ "
        layer = f"{prefix}{pipe}{self.__class__.__name__}({self.value:.2f}) id:({self.node_id})"
        return [layer]
    
    def __str__(self): 

        return f"CRnum({self.value:.2f})"
    

    def __add__(self, target):
        if target > self:
            return target + self
        elif isinstance(target, CRnum):
            return CRnum(self.value + target.value)

    def __mul__(self, target):
        if target > self:
            return target * self
        elif isinstance(target, CRnum):
            return CRnum(self.value * target.value)
        
    def __pow__(self, target):
        if isinstance(target, CRsum):
            result =  CRprod(target.order, len(target))
            for i in range(len(target)):
                result[i] = self ** target[i]
            return result
        elif isinstance(target, CRnum):
            return CRnum(self.value ** target.value)
        else:
            return CREpow(self.copy(), target.copy())


    def sin(self):
        return CRnum(sin(self.value))

    def cos(self):
        return CRnum(cos(self.value))

    def cot(self):
        return CRnum(1 / tan(self.value))

    def tan(self):
        return CRnum(tan(self.value))

    def log(self):
        return CRnum(log(self.value))

    def exp(self):
        return CRnum(exp(self.value))

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
    

    
            
        

