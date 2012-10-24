"""Voronoi Game Play Sample Main
By Xiang Zhang  and Rahul Manghwani @ New York University
"""

from game import Point, Points, Voronoi, Game

def reverse(Points):
    for p in Points:
        if p.s == 0:
            p.s = 1
        else:
            p.s = 0

if __name__ == '__main__':
    STEPS = 10
    #Initialize a points collection
    #Point(x,y,s): s == 0 is self point, s == 1 is opponent point
    #You must make sure there is no two points of the same position!
    points = Points();

    game = Game(steps = STEPS)
    
    for i in range(STEPS):
        print("Playing red for round {}".format(i))
        pt = game.Play(points)
        points.append(Point(pt[0],pt[1],0))
        vor = Voronoi(points)
        print("Red placed a stone at {}".format(pt))
        print("Current area: {}".format(game.Area(points, vor.polygons)))
        game.Draw(points, vor.polygons)
        
        print("Playing blue for round {}".format(i))
        reverse(points)
        pt = game.Play(points)
        points.append(Point(pt[0],pt[1],0))
        reverse(points)
        vor = Voronoi(points)
        print("Blue placed a stone at {}".format(pt))
        print("Current area: {}".format(game.Area(points, vor.polygons)))
        game.Draw(points, vor.polygons)
    
    areas, areao = game.Area(points,vor.polygons)
    if areas > areao:
        print("Red wins at {}!".format(areas/1e6))
    else:
        print("Blue wins at {}!".format(areao/1e6))
    
