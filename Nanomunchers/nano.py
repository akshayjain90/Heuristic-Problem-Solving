""""
Nanomunchers Game Play Algorithm
By Xiang Zhang and Rahul Manghwani @ New York University

Version 0.5, 11/11/2012
"""

import random
import math
import time
import itertools

LEFT = 0
UP = 1
RIGHT = 2
DOWN = 3

def dirtostr(d):
    if d == LEFT:
        return "L"
    elif d == UP:
        return "U"
    elif d == RIGHT:
        return "R"
    elif d == DOWN:
        return "D"
    
class Log(object):
    #Logger
    def __init__(self, name = ""):
        self.name = name
        
    def digest(self, message):
        """Receive an error message and digest it"""
        print(time.strftime("[%d/%b/%Y:%H:%M:%S] {} ".format(self.name), time.localtime()) + message)

class Node(dict):
    """A node object"""
    def __init__(self, i = 0, x = 0, y = 0, s = -1):
        """Constructor
        i: The node id
        x: the node's x location
        y: the node's y location
        s: whether available (-1) or eaten (0 - aten by self, positive - aten by other opponents)"""
        self.i = i
        self.x = x
        self.y = y
        self.s = s
        #Free degree of this node
        self.d = 0
        #Weight of this node
        self.w = 0
        
    def connect(self, node):
        """Connect self to a node.
        node: a node object that this node tries to connect to. Direction is automatically figured out."""
        if node.x > self.x and node.y == self.y and self.get(RIGHT) == None:
            """n goes left"""
            self[RIGHT] = node
            if self.s == -1 and node.s == -1: self.d = self.d + 1
        elif node.x < self.x and node.y == self.y and self.get(LEFT) == None:
            """n goes right"""
            self[LEFT] = node
            if self.s == -1 and node.s == -1: self.d = self.d + 1
        elif node.x == self.x and node.y > self.y and self.get(UP) == None:
            """n goes up"""
            self[UP] = node
            if self.s == -1 and node.s == -1: self.d = self.d + 1
        elif node.x == self.x and node.y < self.y and self.get(DOWN) == None:
            """n goes down"""
            self[DOWN] = node
            if self.s == -1 and node.s == -1: self.d = self.d + 1
        else:
            """Error: n does not go to any direction"""
            raise ValueError("Wrong node n to connect to self: ({0},{1}), n: ({2},{3})".format(self.x,self.y,node.x,node.y))
        
    def mark(self, s):
        """Mark this node
        s: the owner property"""
        #Update other's degree
        if(self.s == -1 and s != -1):
            for k in self:
                if self[k].s == -1:
                    #A free node
                    self[k].d = self[k].d - 1
            self.d = 0
        self.s = s
        
    def dprop(self, D, t):
        """Degree propagation starting on self
        D: the maximum depth
        t: the width of weights"""
        #A queue
        q = list()
        #A set
        m = set()
        #Enqueue self
        if D >= 0:
            m.add(self.i)
            q.append((0,self))
        #Initialize weight
        self.w = 0
        #The main loop of breadth-first search
        while len(q) > 0:
            #Dequeue
            d,n = q.pop(0)
            #Add it's weight
            self.w = self.w + Node.dweight(float(d), float(t))*float(n.d)
            #Check all the neighbours for depth d + 1
            d = d + 1
            if d <= D:
                #Loop over all the orientation
                for o in (LEFT, UP, RIGHT, DOWN):
                    #Get the node
                    c = n.get(o)
                    #If not empty, not aten and not in m, append it
                    if c != None and c.s == -1 and c.i not in m:
                        m.add(c.i)
                        q.append((d,c))
        #Return the weight
        return self.w
                        
        
    @staticmethod
    def dweight(d, t):
        """The weight for depth
        d: the depth
        t: the width"""
        return math.exp(-d*d/t/t)
        
    def __str__(self):
        """To print nicely"""
        return "(i: {0}, x: {1}, y: {2}, s: {3}, d: {4}, L: {5}, U: {6}, R: {7}, D: {8})".format(self.i, self.x, self.y,
                                                                                                 self.s, self.d,
                                                                                                 self[LEFT].i if self.get(LEFT) != None else None,
                                                                                                 self[UP].i if self.get(UP) != None else None,
                                                                                                 self[RIGHT].i if self.get(RIGHT) != None else None,
                                                                                                 self[DOWN].i if self.get(DOWN) != None else None)

class Edge():
    """An edge object"""
    def __init__(self, n1 = 0, n2 = 0):
        """Constructor
        n1: a node id of the edge
        n2: another node id of the edge"""
        self.n1 = n1
        self.n2 = n2
    
    def __str__(self):
        """To print nicely"""
        return "(n1:{0}, n2:{1})".format(self.n1, self.n2)
    
class Graph(dict):
    """A graph object"""
    def __init__(self, nodes = [], edges = []):
        """Constructor
        nodes: a list of Node objects
        edges: a list of Edge objects"""
        for n in nodes:
            dict.__setitem__(self,n.i, n)
        for e in edges:
            self[e.n1].connect(self[e.n2])
            self[e.n2].connect(self[e.n1])
            
    @property
    def ratio(self):
        """Pseudo-property: get the ratio of each player's occupied nodes"""
        r = dict()
        r[-1] = 0
        r[0] = 0
        for k in self:
            if r.get(self[k].s) == None:
                r[self[k].s] = 1.0/float(len(self))
            else:
                r[self[k].s] = r[self[k].s] + 1.0/float(len(self))
        return r
    
    def dprop(self, D, t):
        """Run weight propagation on the graph
        a dictionary of normalized weights for each node is returned
        D: the maximum depth to use
        t: the tau of width"""
        w = dict()
        s = 0.0
        for i in self:
            w[i] = self[i].dprop(D,t)
            s = s + w[i]
        if s != 0:
            for i in w:
                w[i] = w[i]/s
        return w
            
    def copy(self):
        """Return a graph object exactly same as this one"""
        g = Graph()
        #Copy nodes
        for k in self:
            g[k] = Node(self[k].i, self[k].x, self[k].y, self[k].s)
        #Copy edges
        for k in self:
            for kd in self[k]:
                g[k].connect(g[self[k][kd].i])
        return g
                
            
    def __str__(self):
        """Print nicely"""
        ret = "{"
        for k in self:
            ret = ret + str(k) + ":" + str(self[k]) + ", "
        ret = ret + "}"
        return ret
    

class Muncher(dict):
    """A muncher object"""
    def __init__(self, i = 0, d = UP, seq = (LEFT,UP, RIGHT, DOWN), s = 0):
        """Constructor
        i: the node that the muncher is at
        d: the muncher's current direction. can be:
            nano.LEFT
            nano.UP
            nano.RIGHT
            nano.DOWN
        seq: the muncher's sequence of direction to follow. A 4 sized tuple with directions
        s: whether is owner of the muncher is us (==0) or elsebody (!=0)"""

        self.i = i
        self.d = d
        self.seq = seq
        self.s = s
        for k in range(4):
            self[seq[k]] = seq[(k+1)%4]
            
    def move(self, g):
        """Really move this nanomuncher. Return ending node id or None
        g: a Graph object. will be modified!"""
        #Get current node
        m = g[self.i]
        #Get current direction
        d = self.d
        #Test on the directions
        for _ in range(4):
            n = m.get(d)
            if n != None and n.s == -1:
                #Update direction to test next
                self.d = self[d]
                #Update index
                self.i = n.i
                #Mark the nodes
                n.mark(self.s)
                #Return the direction
                return d
            #Test next direction
            d = self[d]
        return None
    
    def moveto(self,g,d):
        """Move to direction d. Return d or None if not successful
        g: a Graph object. Will be modified!
        d: the direction to move to"""
        #Get current node
        m = g[self.i]
        #Get the direction node
        n = m.get(d)
        if n != None and n.s == -1:
            #Update direction to test next
            self.d = self[d]
            #Update index
            self.i = n.i
            #Mark the nodes
            n.mark(self.s)
            #Return the direction
            return d
        return None
            
            
    def attempt(self, g):
        """Attempt to move this nanomuncher. Return the moving direction or None
        g: a Graph object. will NOT be modified"""
        #Get current node
        m = g[self.i]
        #Get current direction
        d = self.d
        #Test on the directions
        for _ in range(4):
            #Get the node to test
            n = m.get(d)
            if n != None and n.s == -1:
                #return the direction
                return d
            #Try another direction
            d = self[d]
        return None
    
    def copy(self):
            return Muncher(self.i, self.d, self.seq, self.s)
            
    def __str__(self):
        """To print nicely"""
        ret = "(i: {0}, d: {1}, s: {2}, q: ".format(self.i, dirtostr(self.d), self.s)
        ret = ret + "{"
        for k in self:
            ret = ret + dirtostr(k) + "->" + dirtostr(self[k]) + ","
        ret = ret + "})"
        return ret

class Board():
    """The board object"""
    def __init__(self, g = None, m = []):
        """Constructor
        g: a graph
        m: a list of Muncher object
        n: initial number of munchers available to self"""
        self.g = g
        self.m = m
        
    def move(self):
        """Move one step, with conflicts resolution"""
        #The moves data structure store moves for all nodes
        moves = dict()
        #Iterate over all munchers
        for muncher in self.m:
            #Record the move of this muncher
            move = muncher.attempt(self.g)
            if move != None:
                i = self.g[muncher.i][move].i
                if moves.get(i) == None:
                    moves[i] = list()
                moves[i].append(muncher)
        #Resolve conflicts
        self.m = list()
        for i in moves:
            #Random select
            j = random.randint(0,len(moves[i]) - 1)
            #Make the move
            muncher = moves[i][j]
            muncher.move(self.g)
            #Record as a live muncher
            self.m.append(muncher)
            
    def movesteps(self,n):
        for _ in range(n):
            self.move()
            
    def greedyMuncher(self, i):
        """Return a greedy muncher for node i. Degree propagation must have been executed
        i: a node id"""
        nid = i
        ds = set([LEFT, UP, RIGHT, DOWN])
        seq = list()
        nodes = set()
        nodes.add(i)
        for _ in range(4):
            w = -1
            d = -1
            #Check all the orientation
            for o in ds:
                if self.g[i].get(o) != None and self.g[i][o].s == -1 and self.g[i][o].w > w and self.g[i][o].i not in nodes:
                    #New orientation
                    d = o
                    w = self.g[i][o].w
            #If no direction works, pop all
            if d == -1:
                for o in ds:
                    seq.append(o)
                break
            #Update current node index
            i = self.g[i][d].i
            nodes.add(i)
            #Append the direction to it
            seq.append(d)
            #Remove the direction from ds
            ds.remove(d)
        return Muncher(nid, seq[0], tuple(seq), 0)
    
    def permuteMuncher(self, i, N):
        """Get a muncher by permuting all possible occurances
        i: node id
        N: steps to look ahead"""
        nid = i
        #Generate permutations
        p = itertools.permutations([LEFT, UP, RIGHT, DOWN])
        #For each squence, get the weight it can traverse
        m = None
        w = -1
        for seq in p:
            muncher = Muncher(nid, seq[0], seq, 0)
            nodes = set()
            #Set weight
            wi = self.g[nid].w
            #Set index as start
            i = nid
            #Set direction
            d = muncher.d
            #Add this index
            nodes.add(i)
            for _ in range(N):
                #Test current node
                move = False
                #4 possible moves
                for _ in range(4):
                    if self.g[i].get(d) != None and self.g[i][d].s == -1 and self.g[i][d].i not in nodes:
                        #Add the weight
                        wi = wi + self.g[i][d].w
                        #Update node index
                        i = self.g[i][d].i
                        #Update direction to test next
                        d = muncher[d]
                        #Add this index
                        nodes.add(i)
                        #A move
                        move = True
                    else:
                        break
                if move == False:
                    break
            #If current sequence produced a good muncher
            if wi > w:
                w = wi
                m = muncher
        return m
    
    def randomMuncher(self, i, N, r):
        """Randomly test the muncher on a permutation with probability p
        The muncher is initialized using greedy muncher
        i: node id
        N: number of steps to test
        r: probability of testing a permutation"""
        nid = i
        #Generate permutations
        p = itertools.permutations([LEFT, UP, RIGHT, DOWN])
        #Initialize by greedy muncher
        m = self.greedyMuncher(i)
        nodes = set()
        w = self.g[nid].w
        i = nid
        d = m.d
        nodes.add(i)
        for _ in range(N):
            #Test current node
            move = False
            #4 possible moves
            for _ in range(4):
                if self.g[i].get(d) != None and self.g[i][d].s == -1 and self.g[i][d].i not in nodes:
                    #Add the weight
                    w = w + self.g[i][d].w
                    #Update node index
                    i = self.g[i][d].i
                    #Update direction to test next
                    d = m[d]
                    #Add this index
                    nodes.add(i)
                    #A move
                    move = True
                else:
                    break
                if move == False:
                    break
        for seq in p:
            #Randomly select a seq
            if (random.random() >= r):
                continue
            muncher = Muncher(nid, seq[0], seq, 0)
            nodes = set()
            #Set weight
            wi = self.g[nid].w
            #Set index as start
            i = nid
            #Set direction
            d = muncher.d
            #Add this index
            nodes.add(i)
            for _ in range(N):
                #Test current node
                move = False
                #4 possible moves
                for _ in range(4):
                    if self.g[i].get(d) != None and self.g[i][d].s == -1 and self.g[i][d].i not in nodes:
                        #Add the weight
                        wi = wi + self.g[i][d].w
                        #Update node index
                        i = self.g[i][d].i
                        #Update direction to test next
                        d = muncher[d]
                        #Add this index
                        nodes.add(i)
                        #A move
                        move = True
                    else:
                        break
                if move == False:
                    break
            #If current sequence produced a good muncher
            if wi > w:
                w = wi
                m = muncher
        return m
                
            
    def copy(self):
        """Create a new board and copy the moves and munchers in"""
        g = self.g.copy()
        m = list()
        for muncher in self.m:
            m.append(muncher.copy())
        board = Board(g,m)
        return board
    
    @property
    def ratio(self):
        """The ratio of munchers of each party"""
        r = dict()
        r[0] = 0
        for muncher in self.m:
            if r.get(muncher.s) == None:
                r[muncher.s] = 1.0/float(len(self.m))
            else:
                r[muncher.s] = r[muncher.s] + 1.0/float(len(self.m))
        return r
        
    def __str__(self):
        """To print nicely"""
        ret = "(g: {0}, m: [".format(str(self.g))
        for muncher in self.m:
            ret = ret + " " + str(muncher) + ","
        ret = ret + "])"
        return ret

class Game():
    """The game object"""
    def __init__(self, nodes = [], edges = [], munchers = [], n = {}, N = 5, D = 4, t = 2, M = 10):
        """Constructor
        nodes: a list of nano.Node objects
        edges: a list of nano.Edge objects
        munchers: a list of nano.Muncher objects
        n: the number of munchers each player has
        N: number of steps to simulate
        """
        self.g = Graph(nodes, edges)
        self.b = Board(self.g,munchers)
        self.n = n
        self.N = N
        self.D = D
        self.t = t
        self.M = M
        self.log = Log("GAME")
        
    def play(self):
        """Make a decision. Return a list muncher objects"""
        return self.playBalanced()
    
    def playBalanced(self):
        """Play the algorithm using balanced strategy"""
        m = list()
        muncher = None
        #Ratio of two sides on the the board
        rm = self.b.ratio
        #Difference of available munchers
        s = 0
        for k in self.n:
            s = s + self.n[k]
        ra = self.n[0] - (s-self.n[0])
        #Difference of number of nanomunchers available
        n = min(self.n[0],max(int((1-rm[0]-rm[0])*len(self.b.m)), int(ra))) - 1
        #Move to the step where I should put a muncher
        self.b.move()
        #Simulate the game
        b = self.b.copy()
        b.movesteps(self.N)
        if(self.shouldNewMuncher(b)):
            #Should compute a new muncher
            self.log.digest("Computing a new muncher...")
            #Compute Nodes
            nodes = self.balancedNodes(b)
            self.log.digest("We have nodes: {}".format(str(nodes)))
            #Compute the new muncher
            muncher = self.balancedMuncher(nodes)
            self.log.digest("A new muncher: {0}".format(str(muncher)))
            if muncher != None:
                #Append the new muncher
                m.append(muncher)
                #Append to the board
                self.b.m.append(muncher)
                #Mark for the muncher
                self.b.g[muncher.i].mark(0)
                #Update the number of munchers available to me
                self.n[0] = self.n[0] - 1
        for _ in range(n):
            #Simulate the game
            b = self.b.copy()
            b.movesteps(self.N)
            if(self.shouldNewMuncher(b)):
                #Should compute a new muncher
                self.log.digest("Computing a new muncher...")
                #Compute Nodes
                nodes = self.balancedNodes(b)
                self.log.digest("We have nodes: {}".format(str(nodes)))
                #Compute the new muncher
                muncher = self.balancedMuncher(nodes)
                self.log.digest("A new muncher: {0}".format(str(muncher)))
                if muncher != None:
                    #Append the muncher
                    m.append(muncher)
                    #Append to the board
                    self.b.m.append(muncher)
                    #Mark for the muncher
                    self.b.g[muncher.i].mark(0)
                    #Update the number of munchers available to me
                    self.n[0] = self.n[0] - 1
        return m
    
    def shouldNewMuncher(self, b):
        """Decide whether to put a new muncher
        b: a board after n steps"""
        #No available munchers, place none
        if self.n[0] == 0: return False
        #If all opponents munchers are gone, place a muncher
        s = 0
        for k in self.n:
            s = s + self.n[k]
        s = s - self.n[0]
        if s == 0:
            self.log.digest("Should put a muncher because opponent has no muncher available")
            return True
        #Get the ratio and probability
        r = b.g.ratio
        if r[0] == 0:
            #If my ratio is 0, must place new muncher
            return True
        elif r[0] <= 1-r[-1]-r[0]:
            #If my ratio is worse than the opponent's, place muncher with probability defined
            #by the softmax between the ratio of opponent's occupied nodes, ratio of opponents' munchers
            #and ratio of munchers left for me among all
            pn = (1-r[-1]-r[0])/(1-r[-1])
            pm = 1 - self.b.ratio[0]
            rc = self.b.g.ratio
            pc = (1-rc[-1]-rc[0])/(1-rc[-1])
            pa = self.ratio[0]
            p = math.log((math.exp(pn) + math.exp(pm) + math.exp(pc) + math.exp(pa) ) / 4)
            self.log.digest("Probability: {0:.2f}, {1:.2f}, {2:.2f}, {3:.2f}, {4:.2f}".format(p,pn,pm,pc,pa))
            if(random.random() < p):
                return True
        return False
    
    def balancedNodes(self, b):
        """Sample out a balanced node
        b: a simulated board after N steps"""
        nodes = set()
        if self.g.ratio[-1]*len(self.g) <= self.M:
            #Return all the nodes
            for i in self.g:
                if self.g[i].s == -1:
                    nodes.add(i)
            if(len(nodes) == 0):
                self.log.digest("No nodes available")
                self.log.digest(str(self.b.g))
            return nodes
        #Add nodes of opponent's munchers' route
        for m in self.b.m:
            if m.s != 0:
                d = m.attempt(self.b.g)
                if d != None:
                    nodes.add(self.b.g[m.i][d].i)
        #Degree propagation
        w = self.b.g.dprop(self.D, self.t)
        #Remove all nodes in w that are not marked -1 or marked 0 in the simulated board
        for i in self.b.g:
            if self.b.g[i].s != -1 or b.g[i].s == 0:
                del w[i]
        #Remove all nodes that are already in nodes
        for i in nodes:
            if w.get(i) != None:
                del w[i]
        #Sample the nodes
        while len(w) > 0 and len(nodes) < self.M:
            #Renormalize w
            s = 0.0
            for i in w:
                s = s + w[i]
            if s == 0.0: return nodes
            for i in w:
                w[i] = w[i]/s
            #Compute the cumulative probability
            k = list(w.keys())
            c = dict()
            c[0] = w[k[0]]
            for i in range(1,len(k)):
                c[i] = c[i-1] + w[k[i]]
            #Sample a node
            r = random.random()
            for i in range(len(k)):
                if r < c[i]:
                    nodes.add(k[i])
                    del w[k[i]]
                    break
        return nodes
    
    def balancedMuncher(self, nodes):
        """Get a muncher from the candidates in nodes
        nodes: a set of nodes"""
        m = None
        r = -1
        for i in nodes:
            muncher = self.b.permuteMuncher(i, self.N)
            b = self.b.copy()
            b.m.append(muncher)
            b.movesteps(self.N)
            rat = b.g.ratio
            if rat[0] > r:
                m = muncher
                r = rat[0]
        return m
    
    @property
    def ratio(self):
        """Get the ratio of each party's number of munchers left"""
        r = dict()
        r[0] = 0.0
        s = 0.0
        for k in self.n:
            if r.get(k) == None:
                r[k] = float(self.n[k])
            else:
                r[k] = r[k] + float(self.n[k])
            s = s + float(self.n[k])
        if s != 0:
            for k in r:
                r[k] = r[k]/s
        return r
    
    def __str__(self):
        """To print nicely"""
        return self.b.__str__()
