/* Alpha-beta pruning implementation for NoTipping Game
 * By Rahul Manghwani and Xiang Zhang @ New York University
 * Version 0.2, 10/09/2012
 */



#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <float.h>
#include <limits.h>
#include <time.h>
#include <stdlib.h>
#include "config.h"
#include "approx.h"


#define SC_SUCCESS 0
#define SC_FAILURE -1

//Default Depth of Searching; Change it to go deep
int DEPTH = 2;

//Random ratio for less depth (base 10)
#define DEPTH_RATIO 8

// Alpha Beta algorithm Interfaces

//Returns the maximu score i.e alpha
double prune(config* c, double alpha, double beta);
double prunemax(config* c, int depth, double alpha, double beta);
double prunemin(config* c, int depth, double alpha, double beta);



int main() {
  
  config c;
  config_fscan(&c, stdin);
  srand(time(NULL));
  int max_depth = 1;
  int i, count;
  //Read the Config
  if(c.stage == 0) {
   //Adding Stage 
   count = 0;
   for(i = 1; i <= 12; i++) {
     count = count + config_self(&c, i) + config_opponent(&c, i);
   }	   
   //If count is less than 5 , crucial state of game go deep 
   if(count < 5) {
     max_depth = 3;
   } 
  } else if (c.stage == 1) {
    //Removing Stage 
    max_depth = 3;	
    count = 0;
    for(i = -15; i <=15 ; i++) {
      if(config_board(&c, i) > 0) {
	count = count + 1;
      }	
    }	
    //Depending on number of remaining weights change your depth 
    if(count < 14) {
      //Crucial Stage go to depth 
      max_depth = 15;
    } else if(count < 22) {
      max_depth = 4;	
    } else {
      printf("0,0\n0\n");	
    }

  }

  //Randomize this depth
  if(max_depth > 1) {
    if(rand() < RAND_MAX/10*DEPTH_RATIO) {
      DEPTH = max_depth - 1;			
    } else {
      DEPTH = max_depth;
    }	
  }
 
  //Make your next move now
  printf("%g\n", prune(&c, -DBL_MAX, DBL_MAX));
  return 0;
}


double prune(config* c, double alpha, double beta)
{
  config next;
  int weight = INT_MAX, board = INT_MAX;
  double score;
  int i,j;

  if(c->stage == 0) {
   //Adding Stage 
   for(i = 1; i <= 12; i++) {
     //Check if you have this weight 
     if(config_self(c, i) == 1) {
	for(j = -15; j <= 15; j++) {	
	  //Try this board position
	  if(config_board(c, j) == 0) {
	     config_copy(c, &next);	 
	     config_selfPlace(&next, i, j);
	     if(!config_tip(&next)) {	
		
		//This move didn't cause tipping; Extract the score from each of my min nodes; Choose the child with max score
		score = prunemin(&next, 1, alpha, beta);
		if(score > alpha) {
		  alpha = score;
		  weight = i;
		  board = j;
		}
		//If the score was 1.0. Bingo found one.This is called "Solve Optimization over minimax"
 		if(alpha == 1.0) {
                  printf("%d,%d\n",weight ,board);
		  return alpha;
		}
	     }
	  }
 	}
     }
   }
   
   if(weight == INT_MAX && board == INT_MAX) {
     //No optimal answer found; i.e every move caused a tipping . I will loose just choose a placement
     alpha = -1.0;
     for(i = 1; i <= 12; i++) {
        if(config_self(c, 1) == 1) {
           for(j = -15; j <= 15; j++) {
             //Try this board position
             if(config_board(c, j) == 0) {
		weight = i;
		board = j;
		break;
	     } 
           }
	   break;
	}
     }	
   }
   
  } else if (c->stage == 1) {
   
    //Removing Stage
    for(j = -15; j <=15; j++) {
      if(config_board(c,j) > 0) {
	//There exist a weight at this position
        config_copy(c, &next);
	config_remove(&next, j);
	if(!config_tip(&next)) {
	  //Not tipping ; Compute a score for your min childs
	  score = prunemin(&next, 1, alpha, beta);
	  if(score > alpha) {
	    alpha = score;
	    weight = config_board(c, j);
	    board = j;
	  }
	  if(alpha == 1.0) {	 
	    printf("%d,%d\n", weight, board);
	    return alpha;
	  }
	}
      }
    }

    if(weight == INT_MAX && board == INT_MAX) {
     //No optimal answer found; i.e every move caused a tipping . I will loose just choose a placement
      alpha = -1.0;
      for(j = -15; j <= 15; j++) {
         //Try this board position
         if(config_board(c, j) > 0) {
                weight = config_board(c,j);
                board = j;
                break;
          }
        }
      }

  } else {
    return 0.0;
  }

  printf("%d,%d\n",weight,board);
  return alpha;
}



// Max and Min functions will call themselves recursively
double prunemax(config* c, int depth, double alpha, double beta)
{
  if(depth > DEPTH) {
    //Its time to approx at this level 
    return approx(c,1);
  }

  config next;
  double score = 0.0;
  int i,j,p = 0;
  
  if(c->stage == 0) {
    //Adding Stage	
    p = 0;
    for(i = 1; i <= 12 ; i = i+1) {
      if(config_self(c, i) == 1) {	
   	
	//Try this weight at all positions
        for(j = -15; j <= 15; j++) {
	   if(config_board(c,j) == 0) {	   
	     //There is no weight at this position
             config_copy(c, &next);
	     config_selfPlace(&next, i , j);
	     if(!config_tip(&next)) {		     
		p = 1; //Some Progress
		
		score = prunemin(&next, depth+1, alpha, beta); //Get the scores from all your min childrens and take the max one
		
		if(score > alpha) {
		  //Better score
		  alpha = score;
		}

		if(alpha >= beta) {
		  // During the entire game for every node alpha should be less than beta. Remember this prunemax will be called prunemin
		  // and beta is best possible min value move that it could make. so if this alpha will be greater than that i will never 
		  // make this move. So Cut the search space and just return beta 
		  // Intutively its like I have something better but my opponent will never take this move
		  return beta;
		}
	        else if(alpha == 1.0) {
		  //Found the best possible score; Return it to your opponent; Remember the goal is assume that your opponent will 
		  // make the best possible move and if this move makes me the winner I won't search further because my opponent will know
		  // this and thereby never make this move
		  return alpha;
		}
	     }
	   }
        }  
      }
    }


  } else if (c->stage == 1) {
     // Removing Stage
     p = 0;
    for(j = -15; j <=15; j++) {
      if(config_board(c,j) > 0) {
        //There exist a weight at this position
        config_copy(c, &next);
        config_remove(&next, j);
        if(!config_tip(&next)) {
          //Not tipping ; Compute a score for your min childs
          score = prunemin(&next, depth + 1, alpha, beta);
          if(score > alpha) {
            alpha = score;
          }

	  if(alpha >= beta) {
	    return beta;
          }
          else if(alpha == 1.0) {
            return alpha;
          }

        }
      }
    }
   



  } else {
    //Game Ended
    alpha = 0.0;
  }

  if(p == 0) {
    //I can't make a move so I loose
    alpha = -1.0;
  }

  return alpha;

}




// Max and Min functions will call themselves recursively
double prunemin(config* c, int depth, double alpha, double beta)
{
  if(depth > DEPTH) {
    //Its time to approx at this level 
    return approx(c,0);
  }

  config next;
  double score = 0.0;
  int i,j,p = 0;

  if(c->stage == 0) {
    //Adding Stage      
    p = 0;
    for(i = 1; i <= 12 ; i = i+1) {
      if(config_self(c, i) == 1) {

        //Try this weight at all positions
        for(j = -15; j <= 15; j++) {
           if(config_board(c, j) == 0) {
             //There is no weight at this position
             config_copy(c, &next);
             config_selfPlace(&next, i , j);
             if(!config_tip(&next)) {
                p = 1; //Some Progress

                score = prunemax(c, depth+1, alpha, beta); //Get the scores from all your min childrens and take the max one

                if(score < beta) {
                  //Better score
                  beta = score;
                }

                if(alpha >= beta) {
                  // During the entire game for every node alpha should be less than beta. Remember this prunemax will be called prunemin
                  // and beta is best possible min value move that it could make. so if this alpha will be greater than that i will never 
                  // make this move. So Cut the search space and just return beta 
		  return alpha;
                }
                else if(beta == -1.0) {
                  //Found the best possible score; Return it to your opponent; Remember the goal is assume that your opponent will 
                  // make the best possible move and if this move makes me the winner I won't search further because my opponent will know
                  // this and thereby never make this move
                  return beta;
                }
             }
           }
        }
      }
    }


  } else if (c->stage == 1) {
     // Removing Stage
     p = 0;
    for(j = -15; j <=15; j++) {
      if(config_board(c,j) > 0) {
        //There exist a weight at this position
        config_copy(c, &next);
        config_remove(&next, j);
        if(!config_tip(&next)) {
          //Not tipping ; Compute a score for your min childs
          score = prunemax(&next, depth + 1, alpha, beta);
          if(score < beta) {
            beta = score;
          }

          if(alpha >= beta) {
            return alpha;
          }
          else if(beta == -1.0) {
            return beta;
          }

        }
      }
    }

  } else {
    //Game Ended
    beta = 0.0;
  }

  if(p == 0) {
    //I can't make a move so I loose
    beta = 1.0;
  }

  return beta;

}





