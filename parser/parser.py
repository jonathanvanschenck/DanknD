#%%
import random
import re

class Node:
    def __init__(self, children = []):
        self.children = children
        self.roll
        
    def __repr__(self):
        return "<Node: {}>".format(self.children)
    
    def _string(self):
        raise NotImplementedError("Virtual Method")
    def __str__(self):
        raise NotImplementedError("Virtual Method")
    
    @property
    def roll(self):
        raise NotImplementedError("Virtual Method")
        
    def reroll(self):
        raise NotImplementedError("Virtual Method")
        
    
    
class Modifier(Node):
    def __init__(self,value):
        self.value = value
        Node.__init__(self)
        
    def __repr__(self):
        return "<Modifier: {}>".format(self._string())

    def _string(self):
        return "{:+}".format(self.value)
    def __str__(self):
        return "{0}={1}".format(self._string(),self.value)
        
    @property
    def roll(self):
        return self.value
    
    def reroll(self):
        return self.roll


class Die(Node):
    def __init__(self,d):
        self.d = d
        self.value = None
        Node.__init__(self)
    
    def __repr__(self):
        return "<Die: {}>".format(self.__str__())
    
    def _string(self):
        return "+1d{0}".format(self.d)
    def __str__(self):
        return "{0}={1}".format(self._string(),self.roll)
    
    @property
    def roll(self):
        if self.value is None:
            self.value = random.randint(1,self.d)
        return self.value
    
    def reroll(self):
        self.value = None
        return self.roll
    
class Add(Node):
    def __init__(self,children):
        Node.__init__(self,children)
        
    def __repr__(self):
        string = "+".join([c.__repr__() for c in self.children])
        return "<Add:{0}={1}>".format(string,self.roll)

    def _string(self):
        return "".join([c._string() for c in self.children])
    def __str__(self):
        return "{0}={1}".format(self._string(),self.roll)

       
    @property
    def roll(self):
        return sum(c.roll for c in self.children)
    
    def reroll(self):
        return sum(c.reroll() for c in self.children)

class Dice(Add):
    def __init__(self,num,d):
        self.num = num
        self.d = d
        Add.__init__(self,[Die(d) for _ in range(num)])
        
    def __repr__(self):
        string = sum([c.value for c in self.children])
        return "<Dice: {}>".format(self.__str__())
    
    def _string(self):
        return "+{0}d{1}".format(self.num,self.d)
    def __str__(self):
        return "{0}={1}".format(self._string(),self.roll)

class Select(Node):
    def __init__(self,children,lowIndex,highIndex, function = sum):
        self.li = lowIndex
        self.hi = highIndex
        self.function = function
        self.included = None
        self.excluded = None
        Node.__init__(self,children)
        
    def __repr__(self):
        string = ",".join([c.__repr__() for c in self.children])
        return "<Selection: [{0}] from {1} to {2} = {3}]>".format(string,self.li,self.hi,self.roll)
    
    @property
    def roll(self):
        if self.included is None:
            _children = sorted(self.children,key = lambda c: c.roll)
            self.included = _children[self.li:self.hi]
            self.excluded = _children[:self.li] + _children[self.hi:]
        return self.function(c.roll for c in self.included)
    
    def reroll(self):
        self.included = None
        for c in self.children:
            c.reroll()
        return self.roll
    
class Advantage(Select):
    def __init__(self,d):
        Select.__init__(self,[Die(d),Die(d)],1,2)
        self.d = d
        
    def __repr__(self):
        string = ",".join([c.__repr__() for c in self.children])
        return "<Advantage: [{0}]={1}({2})>".format(string,self.roll,self.exclude[0].roll)

    def _string(self):
        return "+Ad{0}".format(self.d)
    def __str__(self):
        return "{0}={1}".format(self._string(),self.value)
    

class Disadvantage(Select):
    def __init__(self,d):
        Select.__init__(self,[Die(d),Die(d)],0,1)
        self.d = d
        
    def __repr__(self):
        string = ",".join([c.__repr__() for c in self.children])
        return "<Disadvantage: [{0}]={1}({2})>".format(string,self.roll,self.exclude[0].roll)

    def _string(self):
        return "+Ad{0}".format(self.d)
    def __str__(self):
        return "{0}={1}".format(self._string(),self.value)
 
#%%

mod = re.compile("\A([+-]\d+)\Z")
dice = re.compile("\A[+](([AD])|((?!0)[1-9]\d*))d((?!0)[1-9]\d*)\Z")
delim = re.compile("[+-]")
header = {"A":Advantage, "D":Disadvantage}    

def parse_dice(groups):
    try:
        return header[groups[0]](int(groups[-1]))
    except KeyError:
        return Dice(int(groups[0]),int(groups[-1]))

def parse_modifier(groups):
    return Modifier(int(groups[0]))

def roll_parser(string):
    _string = string.replace(" ","")
    _s = ["","+"][_string[0:1]!="+"] + _string
    indicies = [m.span()[0] for m in delim.finditer(_s)]+[len(_s)]
    res = []
    for i in range(len(indicies)-1):
        sub = _s[indicies[i]:indicies[i+1]]
        attempt = mod.match(sub)
        if not attempt is None:
            res.append(parse_modifier(attempt.groups()))
            continue
        attempt = dice.match(sub)
        if not attempt is None:
            res.append(parse_dice(attempt.groups()))
            continue
        raise SyntaxError("Expression {0}=`{1}` unparseable".format(i,sub))
    return Add(res)

rolls = re.compile("[{]([^}]*)[}]")
def Parser(message):
    nmsg = 1*message
    offset = 0
    for match in rolls.finditer(message):
        li,ri = match.span()
        rollstring = match.groups()[0]
        try:
            r = roll_parser(rollstring)
        except SyntaxError as E:
            raise SyntaxError("From `{0}`, {1}".format(rollstring,E.args[0]))
        nrollstring = str(r)[1:]
        nmsg = nmsg[:li+offset] + "{" + nrollstring + "}" + nmsg[ri+offset:]
        offset += len(nrollstring) - len(rollstring)
        match = rolls.search(nmsg)
    return nmsg