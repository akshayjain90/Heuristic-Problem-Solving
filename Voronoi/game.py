import voronoi
import math
import patch
import matplotlib.pyplot
import shapely.geometry
import random

EPS = 1e-4
RATE_MAX = 15

class Point():
    def __init__(self, x = 0, y = 0, s = 0):
        self.x = x
        self.y = y
        self.s = s
    def copy(self):
        return Point(self.x, self.y, self.s)
    def __repr__(self):
        return (self.x,self.y,self.s).__repr__()
        
class Points(list):
    def __init__(self):
        list.__init__(self)
        
    def copy(self):
        pts = Points()
        for item in self:
            list.append(pts, item.copy())
        return pts

class Voronoi():
    def __init__(self, points = None, rec = (0,0,1000,1000)):
        """Constructor
        rec: rectangle of (xmin, ymin, xmax, ymax)"""
        self.rec = rec
        self.eps = 1e-4
        self.vts = None
        self.polygons = None
        self.points = None
        if points != None:
            self.Fortune(points)

    def Fortune(self, points):
        """Generate polygons.
        points: Input point sets
        return list is:
        vertices: All vertices of all the polygon
        polygons: A list of lists, where polygons[i] is a list of vertices for station i."""
        voronoi.Edge.LE = 0
        voronoi.Edge.RE = 1
        voronoi.Edge.EDGE_NUM = 0
        voronoi.Edge.DELETED = {}   # marker value
        siteList = voronoi.SiteList(points)
        context  = voronoi.Context()
        voronoi.voronoi(siteList,context)
        vertices = context.vertices
        lines = context.lines
        edges = context.edges
        has_edge = context.has_edge
        #print(vertices)
        #print(lines)
        #print(edges)
        #Empty vertices
        if len(lines) == 0:
            vts = [(points[0].x,points[0].y)]
            polygons = [[(0,0),(1000,0),(1000,1000),(0,1000)]]
            self.edges = edges
            self.lines = lines
            self.has_edge = has_edge
            self.vertices = list(vts)
            self.polygons = polygons
            self.points = points
            return
        edgedict = dict();
        for e in edges:
            edgedict[e[0]] = (e[1],e[2], True)
        vts = set()
        #Delete edges that are outside the bounding box
        for v in vertices:
            if self.Inrange(v):
                vts.add(v)
        polygons = list()
        for i in range(len(points)):
            cand = set()
            pset = set()
            #Add to candidates. -1 means does not associate with a line
            cand.add((self.rec[0],self.rec[1]))
            cand.add((self.rec[0],self.rec[3]))
            cand.add((self.rec[2],self.rec[1]))
            cand.add((self.rec[2],self.rec[3]))
            #print(has_edge[i])
            for j in range(len(has_edge[i])):
                #Scanning over the lines to determine intersects or candidates
                edge = edgedict[has_edge[i][j]]
                line = lines[has_edge[i][j]]
                #Edge endpoints outside and points to outside where
                #if edge[0] == -1 and edge[1] != -1 and not self.Inrange(vertices[edge[1]]) or (edge[0] != -1 and edge[1] == -1 and not self.Inrange(vertices[edge[0]])):
                    #continue
                #Edge endpoints outside
                if edge[0] != -1 and (not self.Inrange(vertices[edge[0]])):
                    edge = (-1, edge[1])
                if edge[1] != -1 and (not self.Inrange(vertices[edge[1]])):
                    edge = (edge[0], -1)
                if edge[0] == -1 and edge[1] == -1:
                    #Add to point sets because this is the right one
                    pt1,pt2 = self.Intersect(line)
                    #print((points[i],line,edge,pt1,pt2))
                    cand.add(pt1)
                    cand.add(pt2)
                elif edge[0] == -1 or edge[1] == -1:
                    #Add to candidates because one has to be gone. With edge index.
                    pt1,pt2 = self.Intersect(line)
                    #print((points[i],line,edge,pt1,pt2))
                    cand.add(pt1)
                    cand.add(pt2)
                    if edge[0] == -1:
                        cand.add(vertices[edge[1]])
                    else:
                        cand.add(vertices[edge[0]])
                else:
                    #Add both points to cand, if both the points are valid
                    cand.add(vertices[edge[0]])
                    cand.add(vertices[edge[1]])
            #Iterate over all the candidates, determine whether they can be saved
            for c in cand:
                valid = True
                #Iterate through all the lines associated with point i
                for j in range(len(has_edge[i])):
                    line = lines[has_edge[i][j]]
                    if not Voronoi.Sameside(line, (points[i].x,points[i].y),c):
                        valid = False
                        #print((points[i],line,c,valid))
                        break
                    #print((points[i],line,c,valid))
                if valid == True:
                    pset.add(c)
                    vts.add(c)
            #Update polygons
            polygons.append(sorted(list(pset), key = lambda p: Voronoi.Direction((points[i].x,points[i].y),p)))
        self.edges = edges
        self.lines = lines
        self.has_edge = has_edge
        self.vertices = list(vts)
        self.polygons = polygons
        self.points = points
    
    def Intersect(self, line):
        """Return the intersect of a line with the bouding box
        line: a line tuple representing (a,b,c): ax + by = c"""
        cand = set()
        if line[0] == 0 and line[1] != 0:
            #vertical line
            return ((self.rec[0], line[2]/line[1]),(self.rec[2], line[2]/line[1]))
        elif line[0] != 0 and line[1] == 0:
            #Horizontal line
            return ((line[2]/line[0], self.rec[1]),(line[2]/line[0], self.rec[3]))
        elif line[0] !=0 and line[1] != 0:
            #A normal line
            #On the border x = self.rec[0]
            y = (line[2] - line[0]*self.rec[0])/line[1]
            if y >= self.rec[1] and y <= self.rec[3]:
                cand.add((self.rec[0],y))
            #On the border x = self.rec[2]
            y = (line[2] - line[0]*self.rec[2])/line[1]
            if y >= self.rec[1] and y <= self.rec[3]:
                cand.add((self.rec[2],y))
            #On the border y = self.rec[1]
            x = (line[2] - line[1]*self.rec[1])/line[0]
            if x >= self.rec[0] and x <= self.rec[2]:
                cand.add((x,self.rec[1]))
            #On the border y = self.rec[3]
            x = (line[2] - line[1]*self.rec[3])/line[0]
            if x >= self.rec[0] and x <= self.rec[2]:
                cand.add((x,self.rec[3]))
            if len(cand) != 2:
                raise ValueError("Candidates num incorrect line intersection.\n{cand}".format(cand = cand))
            return tuple(cand)
        else:
            #Abnormal line
            raise ValueError("Incorrect line in line intersection.\n{line}".format(line = line))
    
    @staticmethod
    def Sameside(l, p,c):
        """Determine whether point p and c are on the same side
        l: a line tuple (a,b,c): a*x+b*y = c
        p: a point tuple (x,y)
        c: a point tuple (x,y)"""
        if (l[0]*p[0] + l[1]*p[1] <= l[2] + EPS and l[0]*p[0] + l[1]*p[1] >= l[2] - EPS) \
            or (l[0]*c[0]+l[1]*c[1] <= l[2] + EPS and l[0]*c[0]+l[1]*c[1] >= l[2] - EPS):
            #One point is on the line
            return True
        if l[0] == 0 and l[1] != 0:
            #Verticle line
            if math.copysign(1.0, p[1]-l[2]/l[1]) == math.copysign(1.0, c[1]-l[2]/l[1]):
                return True
            return False
        if l[0] != 0 and l[1] == 0:
            #Horizotal line
            if math.copysign(1.0, p[0]-l[2]/l[0]) == math.copysign(1.0, c[0]-l[2]/l[0]):
                return True
            return False
        if l[0] != 0 and l[1] != 0:
            #Normal line
            if math.copysign(1.0, p[1]-(l[2] - l[0]*p[0])/l[1]) == math.copysign(1.0, c[1]-(l[2] - l[0]*c[0])/l[1]):
                return True
            return False
        else:
            raise ValueError("Incorrect line in same side.\n{line}".format(line = l))
        
    @staticmethod
    def Direction(p1,p2):
        return math.atan2(p2[1]-p1[1],p2[0]-p1[0]);
    
    def Inrange(self, p):
        """Whether a point is in range
        p: a tuple (x,y)"""
        return p[0] >= self.rec[0] and p[0] <= self.rec[2] and p[1] >= self.rec[1] and p[1] <= self.rec[3]

class Game(object):
    def __init__(self, steps = 10, rec = (0,0,1000,1000),corr = 5):
        self.steps = steps
        self.rec = rec
        self.corr = corr
        
    def Draw(self, points, polygons):
        """Draw the polygons
        points: A Points() object
        polygons: Polygons generated from points using Voronoi()"""
        fig = matplotlib.pyplot.figure()
        fig.add_subplot(111)
        ax = fig.axes[0]
        for i in range(len(points)):
            #print((points[i],polygons[i]))
            if(len(polygons[i]) < 2):
                continue
            poly = shapely.geometry.Polygon(polygons[i])
            if points[i].s == 0:
                pa = patch.PolygonPatch(poly, fc = 'red',alpha=0.5)
                ax.add_patch(pa)
            else:
                pa = patch.PolygonPatch(poly, fc = 'blue',alpha=0.5)
                ax.add_patch(pa)
            pt = patch.PolygonPatch(shapely.geometry.Point(points[i].x,points[i].y).buffer(4.0),fc = 'black')
            ax.add_patch(pt)
        ax.set_xlim(self.rec[0],self.rec[2])
        ax.set_ylim(self.rec[1],self.rec[3])
        ax.set_aspect(1)
        matplotlib.pyplot.show()
        
    @staticmethod
    def Area(points, polygons):
        """Compute the area
        points: A Points() object
        polygons: Polygons generated from points using Voronoi()"""
        sarea = 0
        oarea = 0
        #print(points)
        for i in range(len(points)):
            #print((i,points[i].x, points[i].y, points[i].s,polygons[i]))
            poly = shapely.geometry.Polygon(polygons[i])
            if points[i].s == 0:
                sarea = sarea + poly.area
            else:
                oarea = oarea + poly.area
        return (sarea, oarea)
    
    def Play(self, points):
        """Play the game
        points: A Points() object"""
        
        #Use pseudo-minimax policy
        return self.PlayPseudominimax(points)
    
    def PlayPseudominimax(self, points):
        """Pseudominimax algorithm to play the game
        points: A Points() object"""
        if len(points) % 2 == 0:
            return self.PlayPseudominimaxFirst(points)
        else:
            return self.PlayPseudominimaxSecond(points)
    
    def PlayPseudominimaxFirst(self, points):
        """Pseudominimax algorithm to play the game
        points: A Points() object"""
        if len(points) == 0: return (random.randint(200,800), random.randint(200,800))
        pts = points.copy()
        vor = Voronoi(points,self.rec)
        maxpt = None
        maxarea = None
        sarea = None
        pts.append(Point(0,0,0))
        vts = list(vor.vertices)
        vts.append((self.rec[0],self.rec[1]))
        vts.append((self.rec[0],self.rec[3]))
        vts.append((self.rec[2],self.rec[1]))
        vts.append((self.rec[2],self.rec[3]))
        for i in range(len(points)):
            if points[i].s == 0: continue
            for j in range(len(vts)):
                pt = Point(round((points[i].x+vts[j][0])/2), round((points[i].y+vts[j][1])/2), 0)
                #Detect whether in range
                if vor.Inrange((pt.x,pt.y)) == False:
                    continue
                #Detect whether this is ini points
                rep = False
                for k in range(len(points)):
                    if points[k].x == pt.x and points[k].y == pt.y:
                        rep = True
                        break
                if rep == True:
                    continue
                #Continue
                pts[len(points)] = pt
                v = Voronoi(pts,self.rec)
                sarea = self.Area(pts, v.polygons)[0]
                if maxarea == None or sarea > maxarea:
                    maxpt = pt
                    maxarea = sarea
        if maxpt != None:
            rep = False
            pos = (maxpt.x, maxpt.y)
            for k in range(len(points)):
                if points[k].x == pos[0] and points[k].y == pos[1]:
                    rep = True
                    break
            while rep == True:
                pos = (maxpt.x + random.randint(-self.corr,self.corr), maxpt.y + random.randint(-self.corr,self.corr))
                rep = False
                for k in range(len(points)):
                    if points[k].x == pos[0] and points[k].y == pos[1]:
                        rep = True
                        break
            return pos
        
        #Everything does not work, then random
        pos = (0,0)
        rep = True
        while rep == True:
            pos = (random.randint(0,1000), random.randint(0,1000))
            rep = False
            for k in range(len(points)):
                if points[k].x == pos[0] and points[k].y == pos[1]:
                    rep = True
                    break
        return pos
    
    def PlayPseudominimaxSecond(self, points):
        """Pseudominimax algorithm to play the game
        points: A Points() object"""
        if len(points) == 0: return (random.randint(200,800), random.randint(200,800))
        pts = points.copy()
        vor = Voronoi(points,self.rec)
        polygons = vor.polygons
        maxpt = None
        maxarea = None
        sarea = None
        rate = 0.90 #float((float(len(points)) / RATE_MAX + 1))/2
        pts.append(Point(0,0,0))
        #vts = list(vor.vertices)
        #vts.append((self.rec[0],self.rec[1]))
        #vts.append((self.rec[0],self.rec[3]))
        #vts.append((self.rec[2],self.rec[1]))
        #vts.append((self.rec[2],self.rec[3]))
        for i in range(len(points)):
            if points[i].s == 0: continue
            for j in range(len(polygons[i])):
                pt = Point(round((rate*points[i].x+(1-rate)*polygons[i][j][0])), round((rate*points[i].y+(1-rate)*polygons[i][j][1])), 0)
                #Detect whether in range
                if vor.Inrange((pt.x,pt.y)) == False:
                    continue
                #Detect whether this is ini points
                rep = False
                for k in range(len(points)):
                    if points[k].x == pt.x and points[k].y == pt.y:
                        rep = True
                        break
                if rep == True:
                    continue
                #Continue
                pts[len(points)] = pt
                v = Voronoi(pts,self.rec)
                sarea = self.Area(pts, v.polygons)[0]
                if maxarea == None or sarea > maxarea:
                    maxpt = pt
                    maxarea = sarea
        if maxpt != None:
            rep = False
            pos = (maxpt.x, maxpt.y)
            for k in range(len(points)):
                if points[k].x == pos[0] and points[k].y == pos[1]:
                    rep = True
                    break
            while rep == True:
                pos = (maxpt.x + random.randint(-self.corr,self.corr), maxpt.y + random.randint(-self.corr,self.corr))
                rep = False
                for k in range(len(points)):
                    if points[k].x == pos[0] and points[k].y == pos[1]:
                        rep = True
                        break
            return pos
        
        #Everything does not work, then random
        pos = (0,0)
        rep = True
        while rep == True:
            pos = (random.randint(0,1000), random.randint(0,1000))
            rep = False
            for k in range(len(points)):
                if points[k].x == pos[0] and points[k].y == pos[1]:
                    rep = True
                    break
        return pos
