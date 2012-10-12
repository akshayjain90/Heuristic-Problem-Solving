/* Approximation function for NoTipping game
 * Rahul Manghwani @ New York University
 * 10/07/2012
 */

#ifndef APPROX_H
#define APPROX_H

#include "config.h"

//The heuristic approximation function. 1 is win, -1 is lose for me, 0 means no idea...
//max is the flag for max/min node. If max is 1, this node is max node.
double approx(config *c, int max);

#endif //APPROX_H
