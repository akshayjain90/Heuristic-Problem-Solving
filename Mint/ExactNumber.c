#include <stdio.h>
#include <limits.h>
#include <float.h>
#include <stdlib.h>

#define SC_DENOM_REJ 2
#define SC_DENOM_END 1
#define SC_SUCCESS 0
#define SC_FAILURE -1

#define MAX_PRICE 99
#define NUM_DENOM 5
#define MAX_DENOM 99
#define MUL_CENTS 5

#define MAX_DIVIDE 5

int denom_lower[NUM_DENOM];
int denom_upper[NUM_DENOM];

int bestExactNumber(int *d, int *c, int *b, int *e, int *g, int*f, double N);
double prunedExactNumber(int *c, int *e, int *g, int*f, double N, double pcost);
int nextDenom(int *d);
int acceptDenom(int *d);
int initAccept();
int exactChange(int *d, int *c, int *b);
double costExactChange(int *c, double N);
double costUpper(double N);
int printCoin(int *b, int i);

int main(int argc, char *argv[]){
  int ret;
  int i = 0, j = 0;
  int c[MAX_PRICE];
  int b[MAX_PRICE];
  int d[NUM_DENOM];
  int e[MAX_PRICE];
  int f[MAX_PRICE];
  int g[MAX_PRICE];
  double N;

  if(argc > 1){
    N = atof(argv[1]);
  } else {
    printf("Error reading parameters\n");
    return SC_FAILURE;
  }

  ret = bestExactNumber(d, c, b, e, g, f, N);

  printf("EXCHANGE_NUMBER:\n");
  printf("COIN_VALUES: %d", d[0]);
  for(j = 1; j < NUM_DENOM; j = j + 1){
    printf(",%d", d[j]);
  }
  printf("\n");

  for(i = 0; i < MAX_PRICE; i = i + 1){
    printf("%d:", i + 1);
    if(g[i] == 100){
      printf("100");
    } else {
      printCoin(b,g[i]);
    }
    printf(";");
    if(f[i] != -1){
      printCoin(b,f[i]);
    }
    printf("\n");
  }

  printf("//\n");

  return 0;
}

/* The algorithm compute best exact number configuration.
 * d is denominator configuration of size NUM_DENOM. c/b is price
 * configuration of size MAX_PRICE. e/g/f is number configuration of size
 * MAX_PRICE*/
int bestExactNumber(int *rd, int *rc, int *rb, int *re, int *rg, int*rf, double N){
  int c[MAX_PRICE];
  int b[MAX_PRICE];
  int d[NUM_DENOM];
  int e[MAX_PRICE];
  int f[MAX_PRICE];
  int g[MAX_PRICE];
  int ret, i = 0, j = 0;
  double pcost = DBL_MAX, cost;

  //Initialization
  ret = initAccept();
  for(j = 0; j < NUM_DENOM; j = j + 1){
    d[j] = j + 1;
    rd[j] = d[j];
  }

  while(nextDenom(d) == SC_SUCCESS){
//    printf("%d %d %d %d %d\n",d[0],d[1],d[2],d[3],d[4]);
    if(acceptDenom(d) != SC_SUCCESS){
      continue;
    }
    ret = exactChange(d,c,b);
    /*ret = exactNumber(c,e,g,f);
      cost = costExactChange(e, N);*/
    cost = prunedExactNumber(c,e, g, f, N, pcost);
    if (cost < pcost){
      pcost = cost;
      for(j = 0; j < NUM_DENOM; j = j + 1){
	rd[j] = d[j];
      }
      for(i = 0; i < MAX_PRICE; i = i + 1){
	rc[i] = c[i];
	rb[i] = b[i];
	re[i] = e[i];
	rg[i] = g[i];
	rf[i] = f[i];
      }
    }
  }

  return SC_SUCCESS;
}

/* When exactChange is known, compute the exact
 * number. c is the exactChange, e is returned exact number.
 * Both c and e are integer arrays of size MAX_PRICE*/
double prunedExactNumber(int *c, int *e, int *g, int*f, double N, double pcost){
  int i = 0, j = 0;
  double cost = 0.0;

  //Basically test all possibilities
  for(i = 0; i < MAX_PRICE; i = i + 1){
    e[i] = c[i];
    g[i] = i;
    f[i] = -1;
    for (j = i + 1; j < MAX_PRICE; j = j + 1){
      if(c[j] + c[j-i-1] < e[i]){
	e[i] = c[j] + c[j-i-1];
	g[i] = j;
	f[i] = j-i-1;
      }
    }
    //Test for 100 coin
    if (i < 99 && c[99-i-1] + 1 < e[i]){
      e[i] = c[99-i-1] + 1;
      g[i] = 100;
      f[i] = 99-i-1;
    }

    //Compute the current cost
    if((i+1)%MUL_CENTS == 0){
      cost = cost + N*(double)e[i];
    } else {
      cost = cost + (double)e[i];
    }
    if(cost > pcost){
      break;
    }
  }

  return cost;
}


/* Give the current denom state, correct it be the next denom.
 * This function ensure the last of array d is always the
 * largest. Also, j should be initially called as 0*/
int nextDenom(int *d){
  int i = 0, j = 0;
  int ret = SC_SUCCESS;

  d[NUM_DENOM - 1] = d[NUM_DENOM - 1] + 1;

  //Detect feasibility
  if(d[NUM_DENOM - 1] > MAX_DENOM){
    ret = SC_DENOM_END;
    for(j = NUM_DENOM - 2; j >= 0; j = j - 1){
      if (d[j] + 1 <= MAX_DENOM - NUM_DENOM + j + 1){
	d[j] = d[j] + 1;
	for (i = 1; i < NUM_DENOM - j; i = i + 1){
	  d[j + i] = d[j] + i;
	}
	ret = SC_SUCCESS;
	break;
      }
    }
  }

  return ret;
}


/* Accept a set of denominations by upper and lower bounds */
int acceptDenom(int *d){
  int j;
  for(j = 0; j < NUM_DENOM; j = j + 1){
    if(d[j] < denom_lower[j] || d[j] > denom_upper[j]){
      return SC_DENOM_REJ;
    }
  }
  return SC_SUCCESS;
}

/* Initialize the upper and lower bounds of denominations */
int initAccept(){
  denom_lower[0] = 1;
  denom_upper[0] = 16;
  denom_lower[1] = 8;
  denom_upper[1] = 27;
  denom_lower[2] = 13;
  denom_upper[2] = 33;
  denom_lower[3] = 28;
  denom_upper[3] = 47;
  denom_lower[4] = 31;
  denom_upper[4] = 67;

  return SC_SUCCESS;
}

/* Give the exact change of a denomination d with
 * sub dollar values. Thus, d is an integer array of size
 * NUM_DENOM, and c is an integer array of size MAX_PRICE*/
int exactChange(int *d, int *c, int *b){
  int i = 0, j = 0;

  //Initialize
  for(i = 0; i < MAX_PRICE; i = i + 1){
    c[i] = INT_MAX / MAX_DIVIDE; //Just some large number as infinity...
    b[i] = -1;
  }
  for(j = 0; j < NUM_DENOM; j = j + 1){
    if (d[j] - 1 < MAX_PRICE){
      c[d[j] - 1] = 1;
    }
  }

  //Dynamic Programming
  for(i = 0; i < MAX_PRICE; i = i + 1){
    for (j = 0; j < NUM_DENOM; j =j + 1){
      if (i + d[j] < MAX_PRICE && c[i] + 1 < c[i + d[j]]){
	c[i + d[j]] = c[i] + 1;
	b[i + d[j]] = i; // i+d[j] from i
      }
    }
  }

  return SC_SUCCESS;
}


/* Get the cost of a particular coin denomination. c is ann
 * integer array of size MAX_PRICE. N is the rate on the price
 * of multipliers of MUL_CENTS*/
double costExactChange(int *c, double N){
  int i = 0;
  double ret = 0.0;
  for(i = 0; i < MAX_PRICE; i = i +1){
    if ((i+1) % MUL_CENTS == 0){
      ret = ret + N*(double)c[i];
    } else {
      ret = ret + (double)c[i];
    }
  }
  return ret;
}

/* An upper bound of the cost function */
double costUpper(double N){
  return N*34.0 + 263.001;
}

/* Print the coin */
int printCoin(int *b, int i){
  int j = i;
  while(b[j] != -1){
    printf("%d,", j - b[j]);
    j = b[j];
  }
  printf("%d", j+1);

  return SC_SUCCESS;
}
