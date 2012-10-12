/* Approximation function for NoTipping game
 * By Rahul Manghwani @ New York University
 * 10/07/2012
 */

#include "config.h"
#include "approx.h"
#include <time.h>
#include <stdlib.h>

const int ideal_board_config[] = { 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 3, 11, 12, 0, 12, 11, 0, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 0, 0 };

//Heuristic 1
//(Self Feasible Moves - Opponent Feasible Moves)/ Total No of Moves
// Feasible move means where tipping doesn't happen

//This is time consuming. 
double addHeuristic1(config* c, int max){
   //Value returned will be absolute. If its max node, this config is good then value will be positive. If its min node,
   //and this config is good for min, then value will be negative

   int i,j,vacant_spaces;
   // Compute : Feasible Moves for self
   int self_feasible_moves = 0;
   int self_remaining_moves = 0;
   int opponent_feasible_moves = 0;
   int opponent_remaining_moves = 0;

   //Go through the board and figure out vacant spots
   vacant_spaces = 0; 
   for(i = -15; i <= 15; i = i + 1){
      if(config_board(c, i) == 0) {
	vacant_spaces++; 
      }
   }
   
   for(i = 1; i <= 12; i = i + 1) {
     //Check if self have the weight
     if(config_self(c,i) == 1) {
       self_remaining_moves++;
       //Go through all the possible positions
       for(j = 0 ; j < 31; j++) {
	 if(c->board[j] == 0){
	   //Place it and see if you tip
	   c->board[j] = i;
	   if(config_tip(c) == false) {
	     self_feasible_moves++;
	   }
	   //Now remove the weight
	   c->board[j] = 0;
	 }
       }
     }
     //Check if opponent has this weight
     if(config_opponent(c,i) == 1) {
       opponent_remaining_moves++;
       //Go through all the possible positions
       for(j = 0 ; j < 31; j++) {
	 //Place the weight and see if you tip
	 if(c->board[j] == 0){
	   c->board[j] = i;
	   if(config_tip(c) == false) {
	     opponent_feasible_moves++;
	   }
	   //Now remove the weight
	   c->board[j] = 0;
	 }
       }
     }     
   }
    
    //Need to take the max because one of the players may have played one chance less	    
   if (self_remaining_moves == 0 && opponent_remaining_moves == 0){
     return 0.0;
   } else if (self_remaining_moves > opponent_remaining_moves)
     return (double)(self_feasible_moves - opponent_feasible_moves) /(double)(self_remaining_moves * vacant_spaces);
   else
     return (double)(self_feasible_moves - opponent_feasible_moves)/(double)(opponent_remaining_moves * vacant_spaces);  
}

//(-self_total_weight + opponent_total_weight)/78
//Key is to have less Heavy weights
//Value returned is absolute
double addHeuristic2(config* c, int max){
  int i;
  int self_total_weight = 0;
  int opponent_total_weight = 0;

  for(i = 1; i <= 12; i = i + 1){
    if(config_self(c,i) == 1) {
      self_total_weight += i;
    }
    if(config_opponent(c,i) == 1) {
      opponent_total_weight += i;	
    }
  }

  return (double)(-self_total_weight + opponent_total_weight) / 78.0;
}


//Measure of how far is the config away from ideal one
// Ideal config has more heavy weights near the center
// Value returned is relative
// Larger the difference better is config for current player because other player will be changing the board which is away from ideal
double addHeuristic3(config* c, int max){
  int total_board_weight = 0;
  int curWeight = 0;
  int sum_of_abs_diff = 0;  
  int i;  

  for(i = -15; i <= 15; i = i + 1){
    curWeight = config_board(c, i);
    if(curWeight > 0) {
      //There is a weight 
      total_board_weight += curWeight;
      sum_of_abs_diff += (abs(curWeight - ideal_board_config[i+15]));
    }
  }

  if(total_board_weight == 0){
    return 0.0;
  } else if(max == 1) {
    return ((double)sum_of_abs_diff/(double)total_board_weight);	
  } else {
    return (-1.0 * ((double)sum_of_abs_diff/(double)total_board_weight));
  }

}

// |Sum of two torques| / (Max possible torque)
double addHeuristic4(config* c, int max){
   //(-306 , 6) = 300  is the largest possible sum which is possible  
   if(max == 1) {
     return (double)(abs(config_torqueA(c) + config_torqueB(c))) /(double)300.0;
   } else {
     return -(double)(abs(config_torqueA(c) + config_torqueB(c)))/(double)300.0;
   }
}

// (Feasible Remove Moves/ Total No of weights currently on the board)
// Relative value
double removeHeuristic1(config* c, int max) {
  int i;
  int curWeight = 0;
  int feasible_remove_moves = 0;
  int total_moves = 0;
  for(i = -15; i <= 15; i = i + 1) {
     curWeight = config_board(c, i);
     if(curWeight != 0) {
        total_moves++;
 	//There is a weight at this position. Try Removing it
	c->board[i+15] = 0;
	//Check if the board tipped
        if(config_tip(c) == false) {
	   feasible_remove_moves++;
        }
        //Place the weight back
	c->board[i+15] = curWeight;
     }			
  } 
  if(total_moves == 0){
    return 0.0;
  }else if(max == 1) {
    return ((double)(feasible_remove_moves) / (double)(total_moves));
  } else {
    return (-1.0 * ((double)(feasible_remove_moves) / (double)(total_moves)) );
  }
}

// |Sum of two torques| (max possible sum)
// Relative value
double removeHeuristic2(config* c, int max){
  return addHeuristic4(c,max);
}

//How much away is it from the ideal distribution
//Relative Value
//Almost Same as addHeuristic3
double removeHeuristic3(config* c, int max){
  int total_ideal_board_weight = 0;
  int curWeight = 0;
  int sum_of_abs_diff = 0;
  int i;

  for(i = -15; i <= 15; i = i + 1) {
    curWeight = config_board(c, i);
      if(curWeight != 0) {
        //There is a weight 
        total_ideal_board_weight += ideal_board_config[i+15];
        sum_of_abs_diff += (abs(curWeight - ideal_board_config[i+15]));
      }
  }

  if(total_ideal_board_weight == 0){
    return 0.0;
  } else if(max == 1) {
    return (double)sum_of_abs_diff/(double)total_ideal_board_weight;
  } else {
    return -1.0 * ((double)sum_of_abs_diff/(double)total_ideal_board_weight);
  }


}

//Generates a random no between -1 and 1
double genRandomNo(){
    srand(time(NULL));
    // A random no between -1 and 1
    return 2.0*(double)rand()/(double)RAND_MAX - 1.0;
}

//The heuristic approximation function. 1 is win, -1 is lose for me, 0 means no idea...
//max is the flag for max/min node. If max is 1, this node is max node.
double approx(config *c, int max){

  if(config_tip(c)){
    //If this is a tipping case
    return max==0?1.0:-1.0;
  }
  
  if(c->stage == 0) {
    //Adding Stage ; Equal weight to all 4 heuristics for now. Randomness gets a low weight
    return (0.24 * addHeuristic1(c, max)+ 0.24 * addHeuristic2(c, max) + 0.24 * addHeuristic3(c,max) 
	    + 0.24 * addHeuristic4(c,max) + 0.02 * genRandomNo());
  } else {
   //Removing Stage; Equal weight to all 3 heuristics for now. Randomness gets a low weight
    return (0.33 * removeHeuristic1(c, max) + 0.33 * removeHeuristic2(c, max) + 0.33 * removeHeuristic3(c, max)
	    + 0.01 * genRandomNo());
  }

  //Stage end...
  return 0.0;
}
