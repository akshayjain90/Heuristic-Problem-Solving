Written by : Rahul Manghwani and Xiang Zhang @ New York University
Note: It lacks client required to talk to the server, but contains the core algorithms used.

Dating game : http://cs.nyu.edu/courses/Fall12/CSCI-GA.2965-001/dating.html

Description

Matchmaker M is trying to figure out what kind of person P wants to date. So, M arranges many dates for P. P will report to M how much P likes those dates (score between -1 and 1, where 1 is good and -1 is very bad). P's criteria for liking a date or not depend on the weights P gives to various attributes -- e.g. literary knowledge, ability to solve puzzles, and others. The weights may be positive or negative ranging from -1 to 1 and specified as decimal values having at most two digits to the right of the decimal point, e.g. 0.13 but not 0.134. In each response, P may modify 5% of the criteria (P may choose which ones) by 20% each. For example, if a chosen criterion has a weight of 0.4 in P's original criteria, then P can modify it to any value between 0.4 - (0.2*0.4) and 0.4 + (0.2*0.4). P does these modifications without seeing any information provided by M.

A candidate C has values for each of n (not more than 100) attributes -- each value lies between 0 and 1 inclusive and may be an arbitrary precision number. Given the weights P has assigned to each attribute w1, ..., wn and the values C has for each attribute v1, ..., vn, the score P gives to C is simply the dot product of the two vectors. P must set up his or her weights so (before modification) there is an ideal matching candidate that gets a score of 1 and an anti-ideal candidate that gets a score of -1. No candidate should get a score below -1 or above 1. That is, the sum of P's positive weights (before modification) must be 1 and the sum of the negative weights must be -1. After modification, the sum of the positive weights may no longer be +1 and the sum of the negative weights may no longer be -1. Hence the ideal candidate will consist solely of 1s and 0s.

You will play two roles: P and M. As P you set up your weights meeting the constraints above and send them to the architect. In every round, P may also change the weights though without knowledge of the candiate suggested by M. The architect will then generate 20 candidates with values between 0 and 1. As M you manufacture up to 20 candidates meeting the candidate constraints and receive scores from the architect iteratively. If you receive a score of 1 (using the pre-modification weights) you stop and the architect records how many candidates you required. Otherwise, you receive the score you obtained after your 20 candidates. The value of M is the lexicographic value (score, number of candidates) A player X beats player Y if X obtains a greater score or obtains the same score but with fewer candidates than Y does for X's P.
Architecture Team

Receive weights for P from a file, verify attributes of an ideal candidate and an anti-ideal one (both provided by the player who puts up P). Then the architect generates 20 random candidates and provides those weights and their scores to the matchmaker. These occur without modifications. Then receive iteratively a sequence of candidates from the M player (as well as modification instructions from P) and a conclusion as to weights and as to ideal candidate. Supervise time constraint on the M player. Keep track of how many candidates M has used if successful.

Here is the loop:

until matchmaker has completed 20 candidates or received a score of 1
matchmaker submits a candidate
P submits modification instructions (without knowing anything about the candidate)
architect returns the score after modification and displays the candidates
end until

Matchmaker records score and number of candidates proposed by matchmaker.

Information about P should come in as a file regarding the person but socket regarding the candidates.

Architect should put out the candidate value vector and return the scores. 
