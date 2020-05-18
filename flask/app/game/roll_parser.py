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
        return "<Advantage: [{0}]={1}({2})>".format(string,self.roll,self.excluded[0].roll)

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
        return "<Disadvantage: [{0}]={1}({2})>".format(string,self.roll,self.excluded[0].roll)

    def _string(self):
        return "+Ad{0}".format(self.d)
    def __str__(self):
        return "{0}={1}".format(self._string(),self.value)
#%%

die = "(?![-])[+]([AD])d((?!0)[1-9]\d*)"
ADdie = "(?![-])[+]((?!0)[1-9]\d*)d((?!0)[1-9]\d*)"
mod = "([+-](?!0)[1-9]\d*(?!d))"
result = "[=]([-]{0,1}\d*)\Z"

tot = re.compile("%s|%s|%s|%s" % (ADdie,die,mod,result))
whites = re.compile("\s")
term = re.compile(result)

def preprocess(msg):
    if len(msg) == 0:
        raise SyntaxError("Cannot parse roll of empty string")
    _msg = whites.subn("",msg)[0]
    if not _msg[0] in "+-":
        _msg = "+" + _msg
    return _msg

def validate_error(msg):
    _msg = preprocess(msg)
    i = 0
    for m in tot.finditer(_msg):
        # print(m)
        if m.span()[0] != i:
            raise SyntaxError("Unmatched string segment: {0} to {1} : `{2}`".format(i,m.span()[0],msg[i:m.span()[0]]))
        i = m.span()[1]
    if i != len(_msg):
        raise SyntaxError("Unmatched string segment: {0} to {1} : `{2}`".format(i,len(_msg),_msg[i:]))
    return _msg

def validate(msg):
    _msg = preprocess(msg)
    i = 0
    for m in tot.finditer(_msg):
        # print(m)
        if m.span()[0] != i:
            return False
        i = m.span()[1]
    if i != len(_msg):
        return False
    return True

def parse_match(match_tuple):
    n,d1,AD,d2,m,r = match_tuple
    if not n is None:
        return Dice(int(n),int(d1))
    elif not AD is None:
        return {"A":Advantage,"D":Disadvantage}[AD](int(d2))
    elif not m is None:
        return Modifier(int(m))
    raise SyntaxError("Cannot parse `Result` type")

def to_string(msg):
    _msg = validate_error(msg)
    if term.search(_msg):
        return re.subn("\A[+]","",_msg)[0]
    d_list = [parse_match(m.groups()) for m in tot.finditer(_msg)]
    # print(d_list)
    return re.subn("\A[+]","",Add(d_list).__str__())[0]


roll_string = re.compile("[{]([^}]*)[}]")
def roll_msg(msg):
    _msg = ""
    ori = 0
    for m in roll_string.finditer(msg):
        li,ri = m.span()
        _msg = _msg + msg[ori:li+1] + to_string(m.groups()[0]) + "}"
        ori = 1*ri
    return _msg + msg[ori:]
