''' Dater weight generator : Written by Rahul Manghwani @ New York University 
    Version : 0.1 : 11/16/2012 '''
 
import numpy 
import math
import heapq

class Dater(object):
  def __init__(self, dim = 100, precision = 2):
     """ Constructor 
	 Takes Dimensions as input
     """
     self.dimension = dim
     self.weights = []
     self.precision = math.pow(10,precision)
 
  def gen_split(self, pos_num = 0, neg_num = 0):
     """Uses Gausian Distribution for now with a mean of 0.2 and a variance of 0.5(Need to do experiments) 
        to generate the data """
     positive_weights = numpy.array([numpy.abs(numpy.random.normal(loc = 0.2, scale = 0.5)) for l in range(pos_num)])
     negative_weights = numpy.array([numpy.abs(numpy.random.normal(loc = 0.2, scale = 0.5)) for l in range(neg_num)]) 
     #Need to Normalize them 
     positive_weights = positive_weights / numpy.sum(positive_weights)
     negative_weights = negative_weights / numpy.sum(negative_weights)
     #Get them to the required precision 
     pos_weights_prec = numpy.asarray(positive_weights * self.precision,dtype = int) 
     neg_weights_prec = numpy.asarray(negative_weights * self.precision,dtype = int)
     #Make sure they add up to 1/-1
     #Can be done by adding remaining weight in the last weight 
     pos_weights_prec[-1] = self.precision - numpy.sum(pos_weights_prec[:-1])     
     neg_weights_prec[-1] = self.precision - numpy.sum(neg_weights_prec[:-1])
     #Get them in range between 1 and -1 
     pos_weights_prec = pos_weights_prec / self.precision
     neg_weights_prec = -1.0 * neg_weights_prec / self.precision 
     #Stack them and shuffle 
     w = numpy.hstack([neg_weights_prec,pos_weights_prec])
     numpy.random.shuffle(w)
     #Return w 
     return w


  def get_Weights(self):
     """Heuristically , assuming less positive weights the better. However, note they shouldn't be that low in number"""
     #Decide on no of positive and negative weights.Assume ratio is around approx 35 : 65 : positives : negatives
     pos_num = int(numpy.random.normal(loc = 0.35 * self.dimension, scale = 0.002))
     neg_num = int(self.dimension - pos_num)
     while True:
       w = self.gen_split(pos_num, neg_num)
       if self.sanity_checker(w) == True:
	  break
     #Set the weights 
     self.weights = w
     return self.weights
 
  def sanity_checker(self, w):
     """ Ensures positives sum to 1 and negatives sum to -1 """
     sum_pos = numpy.sum(numpy.array([w1 for w1 in w if w1>=0]))
     sum_neg = numpy.sum(numpy.array([w1 for w1 in w if w1 < 0]))
     assert(sum_pos == 1.0)
     assert(sum_neg == -1.0)
     return True	

  def add_noise(self):
     """ Minimizes the magnitude of 5% of the weights which have the largest absolute value """
     five_percentage = int(math.floor(int(self.dimension * 0.05)))
     if five_percentage == 0:
	#Can't add any noise
	noise = numpy.zeros(self.dimension)
	return noise
     else:
	#Create a noise displacement vector
        noise = numpy.zeros(self.dimension)
	#Copy the absolute weight
	abs_weights = numpy.array([abs(self.weights[i]) for i in range(len(self.weights))])
        #Find out the five_percentage of weights having the largest magnitude
	largest = heapq.nlargest(five_percentage, enumerate(abs_weights), key=lambda x: x[1])
        #Go through the largest elements 
	for l in range(len(largest)):
	   index = (largest[l])[0]
	   if abs(self.weights[index]) >= 0.05:
	      #If not obeyed displacement will be zero
	      #Decrease it's magnitude;Make sure its precision it's two decimals
              #Ensures positives weights are decreased; negative weights are increased
              noise[index] = -1.0 * round(self.weights[index] * 0.2,2)
	#Return the noise vector		   
	return noise

if __name__ == '__main__':
    d = Dater(100)  	
    d.get_Weights()
    print(d.weights)
    print(d.add_noise())
