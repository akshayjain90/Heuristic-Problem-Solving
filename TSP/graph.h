#ifndef KK
#define KK
#endif

#include <stdio.h>
#include <stdlib.h>

#include <vector>
#include <queue>
#include <iostream>
using namespace std;

#define MAXV            10000             /* maximum number of vertices */


typedef struct edgenode {
        int x;
        int y;                          /* adjancency info */
        double weight;                     /* edge weight, if any */
        struct edgenode *next;          /* next edge in list */

	bool operator<(const edgenode& en) const
	{
		return (weight > en.weight);
	}

} edgenode;

typedef struct {
        edgenode *edges[MAXV+1];        /* adjacency info */
        int degree[MAXV+1];             /* outdegree of each vertex */
        int nvertices;                  /* number of vertices in the graph */
        int nedges;                     /* number of edges in the graph */
        int directed;                   /* is the graph directed? */
	double totalWeight;             /* For the MST */
} graph;




void initialize_graph(graph *g,int noVertices, bool directed)
{
	int i;				/* counter */

	g -> nvertices = noVertices;
	g -> nedges = 0;
	g -> directed = directed;
	g -> totalWeight = 0.0;


	for (i=1; i<=MAXV; i++) g->degree[i] = 0;
	for (i=1; i<=MAXV; i++) g->edges[i] = NULL;
}



void insert_edge(graph *g, int x, int y, double weight, bool directed)
{
	edgenode *p;			/* temporary pointer */
        p = (edgenode*)malloc(sizeof(edgenode));	/* allocate storage for edgenode */

	p->weight = weight;
	p->y = y;
	p->next = g->edges[x];
	p->x = x;	

	g->edges[x] = p;		/* insert at head of list */

	g->degree[x] ++;

	g->nedges++;

	if (directed == true)
		insert_edge(g,y,x,weight,false);
	
}

void read_graph(graph *g, bool directed)
{
        int i;                          /* counter */
        int m;                          /* number of edges */
        int x, y;                       /* vertices in edge (x,y) */

        initialize_graph(g, 0, directed);

	printf("Enter the no of vertices and no of edges:\n");
        scanf("%d %d",&(g->nvertices),&m);

		
        for (i=1; i<=m; i++) {
		printf("Enter Edge:\n");
                scanf("%d %d",&x,&y);
                insert_edge(g,x,y,0,directed);
        }
}


void delete_edge(graph *g, int x, int y, bool directed)
{
//        cout << "Removing:" << x << " " << y << endl;
	int i;				/* counter */
	edgenode *p, *p_back;		/* temporary pointers */

	p = g->edges[x];
	p_back = NULL;

	while (p != NULL) 
		if (p->y == y) {
			g->degree[x] --;
			if (p_back != NULL) 
				p_back->next = p->next;
			else
				g->edges[x] = p->next;

			free(p);

			if (directed == true)
		{		delete_edge(g,y,x,false);
				g->nedges--; }
			else
				g->nedges --;

			return;
		}
		else
		{	p_back = p;
			p = p->next;
		}
	printf("Warning: deletion(%d,%d) not found in g.\n",x,y);
}

void print_graph(graph *g)
{

	int i;				/* counter */
	edgenode *p;			/* temporary pointer */

	for (i=1; i<=g->nvertices; i++) {
		printf("%d: ",i);
		p = g->edges[i];
		while (p != NULL) {
			printf(" %d %f",p->y, p->weight);
			p = p->next;
		}
		printf("\n");
	}
}

//Builds a MST and returns a MST as 
void buildMST(graph* g, graph* tree)
{
   int vertices = g->nvertices;

   //Initialize the Tree
   initialize_graph(tree,vertices,false);	

   //Apply the Prims Algorithm

   //Discovered Nodes
   vector<bool> discovered; 
   vector<int> visited;	
   double totalWeight = 0.0;
   discovered.reserve(vertices);
   visited.reserve(vertices);
   priority_queue<edgenode> pQueue;


   for(int i=0;i<vertices;i++)
	discovered[i] = false;

   //Start with First City
   int startingCity = 1;
   visited.push_back(startingCity);
   discovered[startingCity-1] = true;

   int destinationCity = 0;
   double desWeight = 0.0;
   int sourceSelEdge = 0;

   for(int i = 2; i <= vertices; i++)
   {

      //Get the connections from starting point
      edgenode* p =  g ->edges[startingCity];
      while( p != NULL)
      {
	if(!discovered[p->y - 1])
	{
	   pQueue.push(*p);	       
	}		
	p = p->next;	
      }		
      	
      //Remove all the nodes already seen; if all nodes are visited exit
      while(visited.size() != vertices && discovered[(pQueue.top()).y - 1])
	pQueue.pop();


      sourceSelEdge = (pQueue.top()).x;
      destinationCity = (pQueue.top()).y;	
      desWeight = (pQueue.top()).weight;	

      discovered[destinationCity - 1] = true;
      visited.push_back(destinationCity);

      totalWeight += desWeight;

      insert_edge(tree,sourceSelEdge,destinationCity,desWeight,true);
      startingCity = destinationCity;
   }    



}
