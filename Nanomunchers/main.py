#!/home/xz558/.opt/bin/python
"""
Middleware for the Game
By Xiang Zhang and Rahul Manghwani @ New York University

Version 0.1, 11/11/2012
"""        
import sys
import nano
import parser
import subprocess
import socket               # Import socket module
import itertools            # For Parsing String
import sys
import time

"""The (initial total) number of munchers each player has"""
no_nanomunchers = 5
teamName = None

class Log1(object):
    #Logger
    def __init__(self, name = ""):
        self.name = name

    def digest(self, message):
        """Receive an error message and digest it"""
        print(time.strftime("[%d/%b/%Y:%H:%M:%S] {} ".format(self.name), time.localtime()) + message)


class Decision():
   def makeDecision(self, msg = None):
       """A logger to help debugging
       Log(name)
       name: give it a name to identify different parts of your log"""
       log = Log1("DECISION")

       global no_nanomunchers
       """Parse the Msg"""
       	
       p = parser.Parser()
       sexp = p.buildGrammar()
       #print(msg)
       sexpr = sexp.parseString(msg, parseAll=True)
       k = sexpr.asList()
       #print(str(k))
       graph = (k[0][0])[1]	
       living_nano = (k[0][1])[1]
       dead_nano = (k[0][2])[1]
       eaten = (k[0][3])[1]
       #time = (k[0][4])[1]

     

       """Add some nodes
       nano.Node(nodeid,x,y,a)
       nodeid: the id of the node
       x: the x position of the node
       y: the y position of the node
       a: if a = -1, available; if a = 0, aten by self; if a > 0, aten by elsebody. It does NOT matter you mark a node where there is a muncher as aten or not"""
       nodes = []
       nodeToLocMap = {}
       eat_Node_Owner_Map = {}
       for m in range(len(eaten)):
         if(str((eaten[m])[1]) == str(teamName.strip())):
           eat_Node_Owner_Map[int((((eaten[m])[0])[0])[1])] = 0
         else:
           eat_Node_Owner_Map[int((((eaten[m])[0])[0])[1])] = 1
    
       graph_nodes = graph[0][1]
       for node in range(len(graph_nodes)):
          nid = int((graph_nodes[node][0])[1])
 	  if eat_Node_Owner_Map.has_key(nid) == True:
	     eat = eat_Node_Owner_Map.get(nid) 
	  else: 
	     eat = -1
		 
          x = int((((graph_nodes[node][1])[1])[0])[1])
          y = int((((graph_nodes[node][1])[1])[1])[1])
          nodeToLocMap[nid] = (x,y)
          nodes.append(nano.Node(nid,x,y,int(eat)))	 
          #log.digest("Added node: {0}".format(nodes[node]))

       """Add some edges
       nano.Edge(nodeid1,nodeid2)
       nodeid1: a nodeid
       nodeid2: a different nodeid"""
       edges = []
       graph_edges = graph[1][1]	   
       for m in range(len(graph_edges)):
         edges.append( nano.Edge(int((graph_edges[m][0])[1]), int((graph_edges[m][1])[1]) ))
         #log.digest("Added edge: {0}".format(edges[m]))
      
       """Add some munchers
          nano.Muncher(nodeid, current_direction, attempt_sequence, s)
          nodeid: the id of the node that the muncher is at
          current_direction: one of {nano.LEFT, nano.UP, nano.RIGHT, nano.DOWN}. This direction will be first tested when the muncher moves
          attempt_sequence: a 4-tuple of distinct directions
          s: 0 means this muncher belongs to self, otherwise opponent."""
    
       """The current rest number of munchers each player has"""
       """ This will be the (Total - dead - living) """
       n = dict()
       n[0] = no_nanomunchers
       n[1] = no_nanomunchers
       #n = [no_nanomunchers,no_nanomunchers]
	
       for m in range(len(dead_nano)):
         if(((dead_nano[m])[3])[1] == str(teamName.strip())):
 	   n[0] = n[0] - 1
         else:
	   n[1] = n[1] - 1
	
       #log.digest("N : {0}".format(str(n))
       munchers = []
       for m in range(len(living_nano)):
  	  nodeid = int(((((living_nano[m])[0])[1])[0])[1])
	  #print(living_nano[m])
	  #Last Direction
	  last_direction = str(((living_nano[m])[1])[1])
	  if last_direction == "Right":
	    last_direction = nano.RIGHT
	  elif last_direction == "Left":
	    last_direction = nano.LEFT
	  elif last_direction == "Up":
	    last_direction = nano.UP
	  elif last_direction == "Down":
	    last_direction = nano.DOWN
	  last_direction = int(last_direction)
	  #print(last_direction)
	  #Create a Tuple of Orientation 
	  orient = ((living_nano[m])[2])[1]
	  nano_orient = () 
  	  for o in range(len(orient)):
	    if orient[o] == "Right":
	      nano_orient = nano_orient + (nano.RIGHT,)
	    elif orient[o] == "Left":
	      nano_orient = nano_orient + (nano.LEFT,)
	    elif orient[o] == "Up":
	      nano_orient = nano_orient + (nano.UP,)
	    elif orient[o] == "Down":
	      nano_orient = nano_orient + (nano.DOWN,)		
	  #Find out the current direction
	  for o in range(len(nano_orient)):
	     if(int(nano_orient[o]) == last_direction):		 
		current_direction = int(nano_orient[(o+1)%4])
	  #print(current_direction)
	  #Check ownership 
          if str(teamName.strip()) == str(((living_nano[m])[3])[1]):
	    owner = 0
	    n[0] = n[0] - 1
	  else:
	    owner = 1
	    n[1] = n[1] - 1
	  #Append this muncher
	  munchers.append(nano.Muncher(nodeid,current_direction,nano_orient, int(owner)))
	  nodes[nodeid].mark(int(owner))
	  log.digest("Added muncher: {0}".format(str(munchers[m])))
          log.digest("Updated node: {0}".format(str(nodes[nodeid])))

       #for nodeid in range(len(nodes)):
	 #log.digest("Updated node: {0}".format(nodes[nodeid]))

       """Create a game object
       nano.Game(nodes, edges, munchers,n)
       nodes: a list of nano.Node objects
       edges: a list of nano.Edge objects
       munchers: a list of nano.Muncher objects
       n: the (initial total) number of munchers each player has"""
      
       log.digest("N : {0}".format(str(n)))
       game = nano.Game(nodes, edges, munchers, n)
       #log.digest("Game object created: {0}".format(game))
   
 
       """Play the game to produce a new nano.Muncher object or None
       If returned None, meaning do not product a new muncher at current configuration
       muncher.i: the index of the node that the muncher is at
       muncher.d: the direction of the new muncher. rne of {nano.LEFT, nano.UP, nano.RIGHT, nano.DOWN}
       muncher.seq: the sequence of attempt. 4 tuples of values in {nano.LEFT, nano.UP, nano.RIGHT, nano.DOWN}"""
       munchers = game.play()
       #game.M = 5
       if len(munchers) == 0:
          #print("No new muncher now")
	  log.digest("No new muncher now")
	  output = "()\n"
       else:
	  log.digest(str(munchers))
	  output ="("
	  for l in range(len(munchers)):
	     muncher = munchers[l]
	     loc = nodeToLocMap[int(muncher.i)]
	     """For every nanomuncher Need to Generate a Seq in which the nano muncher should move and pass that"""
	     """Last Direction is the 4th direction in this sequence """
	     seq = []
	     """Build an orientation First"""
	     for k in range(len(muncher.seq)):
	       if((muncher.seq)[k] == int(muncher.d)):
	  	  index = k
		  break
	     seq.append(int((muncher.seq)[index]))
	     seq.append(int((muncher.seq)[(index+1)%4]))
	     seq.append(int((muncher.seq)[(index+2)%4]))
             seq.append(int((muncher.seq)[(index+3)%4]))
	     if (seq[3] == nano.LEFT):
	       dr = str("Left")
	     elif (seq[3] == nano.RIGHT):
	       dr = str("Right")
	     elif (seq[3] == nano.UP):
	       dr = str("Up")
	     elif (seq[3] == nano.DOWN):
	       dr = str("Down")

	     seq_str = ""
             for k in range(len(seq)):
	       if ((seq)[k] == nano.LEFT):
	         if k == 0:
	           seq_str = str(seq_str) + "Left"
	         else:
		   seq_str = str(seq_str) + " Left"
	       elif ((seq)[k] == nano.RIGHT):
	         if k == 0:
	            seq_str = str(seq_str) + "Right"
	         else:
	            seq_str = str(seq_str) + " Right"
	       elif ((seq)[k] == nano.UP):
	         if k == 0:
	            seq_str = str(seq_str) + "Up"
	         else:
	  	    seq_str = str(seq_str) + " Up" 
	       elif ((seq)[k] == nano.DOWN):
	         if k == 0:
	            seq_str = str(seq_str) + "Down"
	         else:
	            seq_str = str(seq_str) + " Down"

	     #print(seq_str) 	    
	     output = output + "((current_node((id " + str(muncher.i) + ") (loc((x " + str(loc[0]) + ")(y " + str(loc[1])\
		  + ")))))(last_direction " + str(dr) + ")(precedence(" + str(seq_str) + "))(player " + str(teamName.strip())\
       		  + "))"
          
          output = output +")\n"

       log.digest(" Output: {0}".format(output))
       return output

def main():
   s = socket.socket()         # Create a socket object
   host = socket.gethostname() # Get local machine name

   log = Log1("MAIN")

   global no_nanomunchers
   global teamName
   no_nanomunchers = int(sys.argv[1])
   port = sys.argv[2]
   teamName = str(sys.argv[3])

   log.digest(" Connecting to: {0}".format(str(host) + ":" + str(port) ))
   s.connect((host, int(port)))

   #Send the Join Message to the server
   log.digest(" Sending Teamname")
   teamName = str(teamName) + "\n"
   s.send(teamName)
   log.digest(" Teamname sent")
   
   #Get the ACK from the server
   """ack = s.recv(16)
   print(ack)
   if("NACK:" in ack):
     sys.exit('Something Went wrong while sending teamname')"""
   decider = Decision()
   log.digest(" Got ACK from the server")

   while True:

      msg = s.recv(50000)
      log.digest(" Game Moving Forward")
      #print(str(msg))
      #f = open("temp3.txt","r")
      #msg = f.readline()
      if("wins" in msg or "loses" in msg):
        break;

      #Call the Decision Maker
      output = decider.makeDecision(str(msg)) 
      #Send it to the server
      s.send(output)
      
   

if __name__ == '__main__':
    sys.exit(main())
