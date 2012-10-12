/* Game configuration profile for No Tipping competition
 * By Xiang Zhang and Rahul Manghwani @ New York University
 * Version 0.2, 10/08/2012
 */

#ifndef CONFIG_H
#define CONFIG_H

#include <stdio.h>
#include <stdbool.h>

#define CONFIG_SUCCESS 0
#define CONFIG_ERROR -1

   		 
typedef struct __STRUCT_config {
  int stage; //1 indicates adding stage; 0 indicates removig stage
  int board[31]; //0 indicates no weight at this position, else a non zero number represents weight at that position
  int self[12]; //1 indicates whether I still have this weight; 0 indicates otherwise
  int opponent[12]; //Same as self ; but keeps tracks of opponents weights
  int n;  //
}config;


//Initializes the Start of the Game
void config_start(config* a);
//Copies the config from a to b
void config_copy(config* a, config* b); 
//Place a self's weight i at position j
void config_selfPlace(config* a, int i, int j);
//Place a opponent's weight i at position k
void config_opponentPlace(config* a, int i, int j);
//Get the torque at position A i.e for support at position -3
int config_torqueA(config* a);
//Get the torque at position B i.e for support at position -1
int config_torqueB(config* a);
//Check if tipping happens
bool config_tip(config* a);
//Query if self has this weight i ; i =1,2..12
bool config_self(config* a, int i);
//Query if opponent has this weight i ; i = 1,2..12
bool config_opponent(config* a, int i); 
//Query weight at position i in the board ; i = -15..0..15
int config_board(config* a, int i);
//Remove the weight from the position i 
void config_remove(config* a, int i);
//Print the Configuration
void config_print(config* a);
//Print the board
void config_printBoard(config* a);
//Load the config from a file 
void config_fscan(config* a, FILE* f);


#endif  //CONFIG_H

