""" MatchMaker : Written by Rahul Manghwani @ New York University 
    Currently has linear regressor. Plans to Do Perceptron 
    Version : 0.1 : 11/16/2012 """

import numpy 
import time 
import copy
import random

class Log(object):
   #Logger 
  def __init__(self, name = ""):
      self.name = name 
  def digest(self,message):
      """Receive an error message and digest it"""
      print(time.strftime("[%d/%b/%Y:%H:%M:%S] {} ".format(self.name), time.localtime()) + message)


# TO DO: Do experiments to figure out ridge paramater value
class RidgeRegression(object):
  """ Matchmaking using RidgeRegression"""
  def __init__(self, initial_candidates = [], lam = 0.005):
      """Constructor 	
      initial_candidates : A list of tuples (candidate,score);  Candidate is a list; score : float value 
      lam : Regularizer"""
      self.candidates = copy.deepcopy(initial_candidates) 	
      self.dimension = len(candidates[0][0])
      self.w_estimate = numpy.zeros(dimension) 
      self.lam = lam
      #Initialize a random No generator; Uses System Time as seed
      random.seed(None)

  def train(self):
      """Computes the initial weight estimates"""
      #Additional Constraint : Sum of positive and negative weights initially must be 0.
      #Hence, we can add more vectors to refine the subspace 
      for val in numpy.arange(-1.0,1.1,0.10):
         candidate = numpy.ones(self.dimension) * val
	 score = 0.0 
	 self.candidates.append((candidate,score))
	 
      #Create Matrices 
      self.X = numpy.array([c[0] for c in candidates])
      self.Y = numpy.array([numpy.array([c[1]]) for c in candidates])  
  
      #Create Regularization Matrix : It is an identity matrix where every element has a value of 'lam'
      self.R = numpy.identity(self.X.shape[1]) * self.lam
  
      #Solve : Tikhonov regularization : http://en.wikipedia.org/wiki/Tikhonov_regularization
      temp = numpy.dot(self.X, self.X.T) + numpy.dot(self.R.T, self.R)
      self.w_estimate = numpy.dot(numpy.linalg.inv(temp) , numpy.dot(self.X.T, self.Y)).reshape(self.dimension)
   
  def re_estimate(self, candidate, score):
      """Candidate : A list 
	 Score : Float"""
      assert(len(candidate) == self.dimension) 
      #Append it to the existing candidates 
      self.candidates.append((candidate,score))
      #Append it to the existing matrices 
      self.X = numpy.vstack([self.X, candidate])
      self.Y = numpy.vstack([self.Y, numpy.array([score])])  
      #Recalculate the Regularization Matrix 
      self.R = numpy.identity(self.X.shape[1]) * self.lam	
      #Recompute 	      
      temp = numpy.dot(self.X, self.X.T) + numpy.dot(self.R.T, self.R)
      self.w_estimate = numpy.dot(numpy.linalg.inv(temp) , numpy.dot(self.X.T, self.Y)).reshape(self.dimension)
     
  def find_candidate(self):
      """ Tries to suggest an ideal candidate
   	  Ensures the candidate is unique
      """
      #Get a candidate 
      #Choose only positive weights from current weight estimate
      while True:
         proposed_cand = numpy.array(self.w_estimate > 0.0 ,dtype = float).reshape(self.dimension)
	 #Making sure values are between 0 and 1 
	 proposed_cand = proposed_cand % 1.00001
	 if check_uniqueness(proposed_cand) == False:
	    #Not Unique ; Add noise to it
	    proposed_cand = add_noise(self.w_estimate)
	    if check_uniqueness(proposed_cand) == True:
	       #Unique;
	       return proposed_cand
	 else:
	    return proposed_cand         	
	 

  
  def __check_uniqueness(self, proposed_cand = []):
      #Check for uniqueness 
      for cand in self.candidates:
        if ((cand[0] == proposed_cand) == True):
           return False   
       

    
  def __add_noise(self, proposed_cand = []):
      """ Add's noise to the proposed candidate 
      Ensures that proposed values are between 0.0 and 1.0 
      Note: Reason for picking positive weights maximizes the score. Person can add noise. If noise gets added to negative weights,
      that won't affect score of candidate because we won't consider that weight if it in inturn becomes positive we would take it"""
      #Copy 
      candidate = proposed_cand.copy()
      #Generate Gausian Noise with mean 0 and variance 1
      g_noise = numpy.random.normal(self.dimension)
      #We can tweak 5% of the weights.
      change = 	numpy.asarray(numpy.abs(g_noise) > 2.0, dtype = float)
      #Add 20% noise +/- randomly at each of the specified indexes 
      for i in range(len(change)):
         if change[i] > 0.0:
            #Add noise at this index randomly 
	    if random.random() > 0.5:
	      #Increase the weight at this index by 20%
	      candidate[i] = candidate[i] + (candidate[i] * 0.2)
	    else:
	      #Decrease the weight at this index by 20%
	      candidate[i] = candidate[i] - (candidate[i] * 0.2)          
      #Consider only positive weights  
      noisy_cand = numpy.array(candidate > 0.0 ,dtype = float).reshape(self.dimension)
      #Making sure values are between 0 and 1 
      noisy_cand = noisy_cand % 1.00001              	
      #Return the Candidate
      return noisy_cand
       
