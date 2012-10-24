#!/home/xz558/.opt/bin/python -u                                                                                                               
"""Middleware for Voronoi
"""

import time
import sys
from game import Point, Points, Voronoi, Game


def main():
  if len(sys.argv) == 1:
    print 'Usage: ./dummy.py TEAM_NAME'
    sys.exit(1)
  print sys.argv[1]


  STEPS = 7
  #Initialize a points collection
  #Point(x,y,s): s == 0 is self point, s == 1 is opponent point

  game = Game(steps = STEPS)
  #Maintains a list of positions. 
  #Update a list on seeing an opponent's move and self's choosen move
  points = Points()

  while True:
    try:
      s = raw_input()
    except EOFError:
      # print "EOFError"
      # Don't pollute output, output anything to stderr.
      break;

    #Indicates Game Over
    if ("Game Over:" in s or "Wins" in s):
      break

    # Get the first tuple of the server input
    tuples = s.split()
    
    if len(tuples):
      #Get opponent's move; It will be at the start 
      ftuple  = tuples[0]
      p = ftuple.split(',')
      opp_x  = int(p[0])
      opp_y  = int(p[1])
      #Client makes sure there are no two stones on the same position. 
      #Server does this job so its needless. Will remove it later
      for k in range(len(points)):
	if points[k].x == opp_x and points[k].y == opp_y:
	   print "Error! You can only put one stone at a position"
	   break
      ####
      points.append(Point(opp_x,opp_y,1))
      pt = game.Play(points)        			
    else:
      #Game started.You make the very first move
      pt = game.Play(points)
       	
    #Record your move
    points.append(Point(pt[0],pt[1],0))

    #Write to Stdout
    print "%d,%d " % (pt[0], pt[1])

        
    

if __name__ == "__main__":
  main()
    
