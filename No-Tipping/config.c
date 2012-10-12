/* Game configuration profile for No Tipping competition
 * By Xiang Zhang and Rahul Manghwani @ New York University
 * Version 0.2, 10/08/2012
 */

#include <stdio.h>
#include <stdbool.h>
#include "config.h"

//The game start configuration
void config_start(config *c)
{
   int i;
   c->stage = 0;
   for (i = 0; i< 31; i++)
      c->board[i] = 0;
   for(i = 0 ; i < 12; i++)
   {
      c->self[i] = 1;
      c->opponent[i] = 1;
   }
   
   c->board[-4+15] = 3;
   c->n = 24;	
}

//Copy config a to config b
void config_copy(config *a, config *b)
{ 
   int i;
   b->stage = a->stage;
   b->n = a->n;
   for(i = 0; i < 12; i++)   
     b->self[i] = a->self[i];
   for(i = 0; i < 12; i++)	
     b->opponent[i] = a->opponent[i];	
   for(i = 0; i < 31; i++)
     b->board[i] = a->board[i];
}

//Compute the torque of the first support at -3
int config_torqueA(config *a)
{
  int ret = 9;
  int i;

  for(i = -15; i<=15; i++)
  {
    ret = ret + (i + 3) * config_board(a,i);
  }
  return ret;
}

//Compute the torque of the second support at -1
int config_torqueB(config *a)
{
  int ret = 3;
  int i;

  for(i = -15; i<=15; i++)
  {
    ret = ret + (i + 1) * config_board(a,i);
  }
  return ret;
}


//Judge whether a config has caused tipping. True if tipped
bool config_tip(config *c)
{
  if(config_torqueA(c) < 0 || config_torqueB(c) > 0) {
    return true;
  }
  return false;
}

//Query the configuration at position i. Return a weight. i = -15,...,15
int config_board(config *c, int i)
{
  return c->board[i+15];
}


//Query whether myself has weight i. i = 1...12
bool config_self(config *c, int i)
{
  if(c->self[i-1] == 1) {
    return true;
  }
  return false;
}


//Query whether opponent has weight i. i = 1...12
bool config_opponent(config *c, int i)
{
  if(c->opponent[i-1] == 1) {
    return true;
  }
  return false;
}

//Place a self weight i to position j
void config_selfPlace(config *c, int i, int j)
{
   c->self[i-1] = 0;
   c->board[j+15] = i;
   c->n = c->n -1; 
   if (c->n == 0) {
     c->stage = 1;
   }
     
}

//Place an opponent weight i to position j
void config_opponentPlace(config *c, int i, int j)
{
   c->opponent[i-1] = 0;
   c->board[j+15] = i;
   c->n = c->n -1;
   if (c->n == 0) {
     c->stage = 1;
   }
}


//Remove a weight from position i
void config_remove(config *c, int i)
{
  c->board[i + 15] = 0;
  c->n = c->n + 1;
  if(c->n == 25)
  {
    c->stage = 2; 	
  }
}

//Print a config
void config_print(config *c){
  int i;
  printf("%d\n", c->stage);
  for(i = -15; i <= 15; i = i + 1){
    printf("%d ", config_board(c,i));
  }
  printf("\n");
  for(i = 1; i <= 12; i = i + 1){
    printf("%d ", config_self(c,i)?1:0);
  }
  printf("\n");
  for(i = 1; i <= 12; i = i + 1){
    printf("%d ", config_self(c,i)?1:0);
  }
  printf("\n");
  printf("%d %d\n", config_torqueA(c), config_torqueB(c));
  printf("%d\n", c->n);
  printf("%s\n", config_tip(c)?"Tipped":"Good");
}

//Print the board only
void config_printBoard(config *c){
  int i;
  for(i = -15; i <= 15; i = i + 1){
    printf("%d ", config_board(c,i));
  }
  printf("\n");
}

//Read in a config
void config_fscan(config *c, FILE* f){
  int i; 
  //Read the stage 
  fscanf(f, "%d", &c->stage);
  //Read the board config
  for(i = 0; i < 31; i++) {
   fscanf(f, "%d", &c->board[i]);
  } 
  //Read in self weights
  for(i = 0; i < 12; i++) {
    fscanf(f, "%d", &c->self[i]);
  }
  //Read in opponent weights
  for(i = 0; i < 12; i++) {
    fscanf(f, "%d", &c->opponent[i]);
  }
  //Set c->n
  if(c->stage == 0) {
    for (i = 1; i < 12; i++) {
       if(c->self[i] == 1) {
	 c->n = c->n + 1;
       }
       if(c->opponent[i] == 1) {
	 c->n = c->n + 1;
       }	
    }
  } else if(c->stage == 1) {
    c->n = 0;	
    for(i = 0; i < 31; i++) {
      if(c->board[i] < 0) {
	c->n = c->n + 1;
      } 	
    }

    c->n = 25 - c->n; 
  } 
}
