Voronoi Game written by : Xiang Zhang and Rahul Manghwani @ New York University

 Given a set of point-sized stones (which we will call ``stones'' for simplicity), a Voronoi diagram is a tesselation of a plane into polygons such (i) that every stone is in the interior of one polygon and (ii) for every point x in the polygon P associated with stone s, x is closer to s than it is to any other stone s'. Distance is based on Euclidean distance.

The Voronoi game is a two person game that works as follows: you and I each start with N stones (should be a command line parameter throughout -- no magic numbers in your programs please). Yours are red and mine are blue. The first player places one stone, then the second player places one stone and play alternates with each player placing one stone until the second player places the last stone.

As the game proceeds, the Voronoi diagram is computed with red polygons surrounding red stones and blue polygons surrounding blue stones. The display should make the stones darker than the other points in the polygon. 

http://cs.nyu.edu/courses/Fall12/CSCI-GA.2965-001/voronoi.html
