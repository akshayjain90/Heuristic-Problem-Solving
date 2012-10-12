/* Author : Rahul Manghwani @ New York University
   Travelling Salesman Problem : Uses Christophides approximation and 2 opt heuristic.
   Solution is within 1.2 to 1.3 % of optimal 
*/

#ifndef KK
 #define KK
 #include "graph.h"
#endif


#include <algorithm>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
#include <stdlib.h>
#include <map>
#include <string.h>
#include <sstream>
#include <math.h>
#include <set>
#include "PerfectMatching.h"
#include <stdio.h>


#define SUCCESS 0
#define FAILURE -1

using namespace std;

//Does a Euler Tour on the graph and returns the edges 
vector<int> EulerTour(graph* mg);
void doTwoOptimization(vector<int>& tour, map<int, map<int,double> >& cityToOtherCities );



int main(int argc, char* argv[])
{

  ifstream input;
  string line;
  map<int,vector<double> > cities;
  map<int, map<int,double> > cityToOtherCities;
  graph g;
  ofstream output("TSPData.txt");
 
  if(argc > 1)
  {
    input.open(argv[1]);
  }
  else
  {
    printf("Error reading parameters\n");
    return FAILURE;
  }


  while ( input.good() )
  {
      getline (input,line);
      stringstream iss(line);
      vector<double> cityInfo; 
      while(iss)
      {
	string s;
	iss >> s;
        if(s.empty())
         break;
	 
	cityInfo.push_back(atof(s.c_str()));
      }

      if(!cityInfo.empty())
      {
        int cityId = (int)cityInfo.at(0);
        cityInfo.erase(cityInfo.begin());
        cities.insert(pair<int,vector<double> > (cityId,cityInfo));
      } 
  }

  
  for(map<int, vector<double> >::iterator it = cities.begin(); it != cities.end(); it++)
  {
     int cityId = (*it).first;
     vector<double> citySource = (*it).second;
     vector<double>::iterator sorIt = citySource.begin();
     map<int, double> desCities;		
     for(map<int, vector<double> >::iterator it1 = cities.begin() ; it1 != cities.end(); it1++)
     {
	double distance = 0.0;
	if(cityId != (*it1).first)
	{
	   //It shouldn't be the same city
	   vector<double> cityDes = (*it1).second;
	   for(vector<double>::iterator desIt = cityDes.begin(); desIt != cityDes.end(); desIt++)
	   {
		distance += pow(*desIt - *sorIt,2);
		sorIt++;
	   }

	   //Set the Source Iterator to begin for next city
	   sorIt = citySource.begin();
	   distance = sqrt(distance);
	   desCities.insert(pair<int,double> ((*it1).first,distance));
	}
     }

     cityToOtherCities.insert(pair<int, map<int,double> > (cityId, desCities));
     
  }

/* 
  for(map<int, map<int,double> >::iterator it = cityToOtherCities.begin();  it != cityToOtherCities.end(); it++)
  {
        map<int,double>::iterator itt;
	itt = (*it).second.begin();
	cout << (*itt).second << endl;

  }
  
*/

  initialize_graph(&g,cities.size(),true);
  

  for(map<int, map<int,double> >::iterator it = cityToOtherCities.begin(); it != cityToOtherCities.end(); it++)
  {
     for(map<int, double>::iterator it1 = (*it).second.begin(); it1 != (*it).second.end(); it1++)
     {
	insert_edge(&g,(*it).first, (*it1).first,(*it1).second, true);
     }
  }


/*
//Validate MST
        initialize_graph(&g,8,true);

        insert_edge(&g,1,3,20.0, true);
	insert_edge(&g,1,2,40.0, true);
        insert_edge(&g,1,8,30.0, true);
        insert_edge(&g,1,7,50.0, true);
        insert_edge(&g,1,6,80.0, true);

        insert_edge(&g,2,8,50.0, true);
	insert_edge(&g,8,7,60.0, true);
	insert_edge(&g,6,4,10.0, true);
	insert_edge(&g,6,5,20.0, true);
	insert_edge(&g,4,5,10.0, true);
	
	insert_edge(&g,8,5,70.0, true);
	insert_edge(&g,6,5,100.0,true);
*/
	
 
   graph t;
   buildMST(&g,&t);
//   print_graph(&subgraph);

   //Finding the Set of Odd Vertices in the MST
   set<int> oddDegVertices;
   edgenode* p;
   int count,i;
   int totalNoOfEdges = 0;
   for(i=1; i <= t.nvertices; i++)	
   {
	count = 0;
	p = t.edges[i];
	while(p!=NULL)
	{
	  count++; 
	  p = p->next;
	}
	if(count%2 !=0)
	{
	  totalNoOfEdges += count;
	  oddDegVertices.insert(i);
	}
   }

   //Map these Odd Degree Vertices to Id's from 0
   map<int,int> changeids;
   map<int,int> newToOld;
   int newCityId = 0;
   for(set<int>::iterator it = oddDegVertices.begin(); it != oddDegVertices.end(); it++)
   {
	changeids[*it] = newCityId;
	newToOld[newCityId] = *it;
	newCityId++;
   }

   //Compute the Perfect Matching Min Weight
   PerfectMatching *pm = new PerfectMatching(oddDegVertices.size(), totalNoOfEdges);



   //Insert all the edges
   p = NULL;
   for (set<int>::iterator it=oddDegVertices.begin(); it != oddDegVertices.end(); it++) {
                p = g.edges[*it];
                while (p != NULL) {
			if( oddDegVertices.find(p->y) != oddDegVertices.end())
			 {
			    pm->AddEdge(changeids[*it], changeids[p->y]  ,p->weight);
			 }
                        p = p->next;
                }
   }

   //Compute 
   pm->Solve();

   //Enter the mappings in the original graph to create a subgraph so that every node has even no of vertices
   int j;
   for(int i=0;i<newCityId;i++)
   {
	j = pm->GetMatch(i);
	if (i<j)
        {
	//	cout << newToOld[i] << ":" << newToOld[j] << "\n" << endl;
		//Weight is irrelevant now so insert a dummy weight
		insert_edge(&t,newToOld[i], newToOld[j], cityToOtherCities[newToOld[i]][newToOld[j]],true);
	}
   }

   delete pm;

  //print_graph(&t);

  // Form a Euler Circuit 
  vector<int> tour = EulerTour(&t);  

  //Hamiltonian Path.
  vector<int> tsp;
  tsp.push_back(tour.at(0));
  for(int i=1;i<tour.size();i++)
  {
    	if( find(tsp.begin(), tsp.end(), tour.at(i)) == tsp.end() )
	{
	  tsp.push_back(tour.at(i));
	}
  }
  tsp.push_back(1);


/*    for(map<int, map<int,double> >::iterator it = cityToOtherCities.begin();  it != cityToOtherCities.end(); it++)
  {
        map<int,double>::iterator itt;
        itt = (*it).second.begin();
        cout << (*itt).second << endl;

  }
*/

  doTwoOptimization(tsp, cityToOtherCities);

  double totalScore = 0;
  for(vector<int>::iterator it = tsp.begin(); it < tsp.end()-1; it++) 
  {
     totalScore = (double)(totalScore + (double)cityToOtherCities[*it][*(it+1)]);
     output << *it << " " << cities[*it].at(0) << " " << cities[*it][1] << " " << cities[*it][2] << endl;
  }
     output << 1 << " " << cities[1][0] << "  " << cities[1][1] << "  " << cities[1][2] << endl;
  cout << endl;
  printf("TotalScore:%f\n",totalScore); 
  output.close();
  return 0;
}

//Perform 2-opt optimization on this tour
//Logic Goes like this 
//Take a list of cities in order of the path
//For each pair of cities, compare their edge to other edges with do not share this pair
//Check if distance of city(c1,c2) + city(c3,c4) > city(c1, c3) + city(c2, c4)
//Check if this would be good swap
//If yes move the cities and reverse the path between them.

void doTwoOptimization(vector<int>& tour, map<int, map<int,double> >& cityToOtherCities ) 
{

   int city1, city2, city3, city4;

   int i,j,k;
   double oldpairsDis = 0.0;
   double newpairsDis = 0.0;
   double reduction, bestReduction = 0.0;
   int bestC1,bestC2,bestC3,bestC4;
   bool swapFound = false;   
   double threshold = 0.1; //How much low the reduction should be
   bool earlyBreak = false;  

for(k = 1; k <=200; k++)
{
   swapFound = false;
   earlyBreak = false;
   bestReduction = 0.0;
   for(i = 0; i < tour.size() - 3; i++) //Going from 0 to 997.
   {
	city1 = tour.at(i);
	city2 = tour.at(i+1);
	
	for(j = i + 2; j + 1 < tour.size() ; j++)
	{
	   city3 = tour.at(j);
	   city4 = tour.at(j+1);

	   oldpairsDis = (double)cityToOtherCities[city1][city2] + (double)cityToOtherCities[city3][city4];
	   newpairsDis = (double)cityToOtherCities[city1][city3] + (double)cityToOtherCities[city2][city4];
		 
           reduction = oldpairsDis - newpairsDis;
	   if(reduction > bestReduction)
	   {
	      //std::cout << "Found a reduction:" << std::endl;
	      bestReduction = reduction;
	      bestC1 = i;
	      bestC2 = i + 1;
	      bestC3 = j;
	      bestC4 = j + 1;		      		
	      swapFound = true;
	      if( reduction/oldpairsDis <= threshold) {
		earlyBreak = true;
		break;
	      } 	      
	   }
	}

	if(earlyBreak == true)
	{
	  break;	
	}
   }

   //Only if the swap was found will be change the tour
   if(swapFound) {
        //std::cout << "Swapping..." << std::endl;		
	//Swap the cities c2 and c3 in place
	int temp = tour.at(bestC2);
	tour.at(bestC2) = tour.at(bestC3);
	tour.at(bestC3) = temp;

	bestC2++;
	bestC3--;
  	//Reverse the path between c2 and c3
	  while (bestC2 < bestC3) 
	  {
		int temp = tour.at(bestC2);
	        tour.at(bestC2) = tour.at(bestC3);
        	tour.at(bestC3) = temp;
		bestC2++;
		bestC3--;
	  }

	  double totalScore;
	  for(vector<int>::iterator it = tour.begin(); it < tour.end()-1; it++)
          {
                totalScore = (double)(totalScore + (double)cityToOtherCities[*it][*(it+1)]);
          }	
      }
   }

}




edgenode* getMinEdge(graph* mg,int curVertex) 
{
  edgenode* start = mg->edges[curVertex];
  if(start->next == NULL)
  {
    return start;
  } 
  else
  {
     double minWeight = start->weight;
     edgenode* minNode = start;
     start = start->next;
     while(start != NULL)
     {
	if(start->weight < minWeight)
	{
	   minWeight = start->weight;
	   minNode = start;
	}
	start = start->next;
     }	
     return minNode;
  }
   
}


int getMaxOutDeg(graph* mg,set<int>& unusedVertexes)
{
   int max = -1;
   int node = -1;
   for(set<int>::iterator it = unusedVertexes.begin(); it!= unusedVertexes.end(); it++)
   {
	if(max < mg->degree[*it])
	{
	   node = *it;
	   max = mg->degree[*it];
	}
   }
   return node;
}

//Linear Time Algorithm based on Hierholzer's algorithm
vector<int> EulerTour(graph* mg)
{
  vector<int> tour;
  edgenode* p = NULL;
  int startVertex = 1;
  set<int> unusedVertices;
  unusedVertices.insert(startVertex);  
  tour.push_back(startVertex);
  int curVertex;  

  while(unusedVertices.size() > 0)
  { 
 
     startVertex = *(unusedVertices.begin());
    // startVertex = getMaxOutDeg(mg, unusedVertices); 

     curVertex = startVertex;
     do {	
	       p = mg->edges[curVertex];
//	       p = getMinEdge(mg,curVertex);
	       if(p != NULL)
	       {
		  tour.push_back(p->y);
		  delete_edge(mg,curVertex,p->y,true);
		  unusedVertices.insert(p->y);		
	
		  if(mg->degree[curVertex] == 0)
		  {
		    //Curvertex is exhausted remove it
		     unusedVertices.erase(curVertex);	
		  }
		
                  curVertex = p->y;
		  if(mg->degree[p->y] == 0)
		  {
		    //Exhausted ? if yes remove it
		     unusedVertices.erase(p->y);
		  }
		  
	       }
	       else
		  break;		       
	
	} while(curVertex != startVertex);
  }

  return tour;
}

