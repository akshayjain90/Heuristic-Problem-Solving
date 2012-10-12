''' Client Middleware talking to server and maintaining game state
    Written by Rahul Manghwani @ New York University
    10/07/2012 '''

#!/usr/bin/python        

import subprocess 
import socket               # Import socket module
import itertools            # For Parsing String
import sys

s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name


port = raw_input("Enter Port: ");

print 'Connecting to ', host, port
s.connect((host, int(port)))


#Send the teamName to the server
teamName = sys.argv[1] + "\n"
s.send(teamName)

print("Teamname sent")
#Accept the Connection Accepted Message
acceptedMsg = s.recv(1024)
print(acceptedMsg)


stage = 0                   #Maintains the Stage of the Game
board = [0] * 31            #Maitains the board configuration
board[11] = 3               #Starting Position. Weight 3 at pos -4
self  = [1] * 12            #Maintains the self weights
opponent = [1] * 12         #Maintains the opponent weights


#State needed in case move was rejected by the server
lastDecidedWeight = 0
lastDecidedPosition = 0

reject = 0 # 1 indicated a reject
justAccept = 0 #1 indicate don' do this
while True:
    
    msg = s.recv(1024)
    msg = msg.rstrip('\n')
    print(msg)


    if("WIN" in msg or "win" in msg or "LOSE" in msg or "lose" in msg or "TIP" in msg or "tip" in msg):
        break;
    
    """ Parse the Msg """
    if(msg == "ACCEPT" or msg == "accept"):
        reject = 0
        justAccept = 1
        pass

    #if(msg == "REJECT" or msg == "reject"):
    if ("REJECT" in msg or "reject" in msg):
        print "Tracked Reject"
        self[int(lastDecidedWeight)-1] = 1 #Undoing 
        board[int(lastDecidedPosition) + 15] = 0
        reject = 1 #Directly make the decision again
    

    if(justAccept == 1):
        #This is a Accept Message. Ignore it
        justAccept = 0
        pass
    else:
        """ Board Message """

        """ Check the first character set the stage"""
        if(msg[0] == 'A' or msg[0] == 'a'):
            stage = 0
        elif(msg[0] == 'R' or msg[0] == 'r' and reject != 1):
            stage = 1
 
        
        """ Extract the board positions """
        msg = msg[msg.find("|") + 1:msg.find("|i")]
    
        """Set up stage"""
        pairs = msg.split()

        if(reject == 0): #Previous Message was accepted
            if(stage == 0):
                #only record the opponent's weight and accordingly set the board positions
                a =[]; # Used to set the indexes back
                for pair in pairs:
                   [weight, position] = pair.split(",")
                   weight = int(weight)
                   position = int(position)
                   if(position == -4):
                       continue #Ignore this
                   if(self[weight-1] == 1):
                       #I still have this weight, This is definitely opponents
                       opponent[weight-1] = 0   #Opponent No Longer has this weight
                       board[position + 15] = weight
                   else:
                       #I am not sure if this mine or opponents
                       if(self[weight-1] == -1): #We are seeing this weight second time so opponent's weight
                           opponent[weight-1] = 0 #Opponent No Longer has this weight
                           board[position + 15] = weight
                       else: #I know I had put this weight, So assume this is mine itself
                           self[weight-1] = -1
                           board[position + 15] = weight #Fixed this bug
                           a.append(weight-1) #Record this position
               
               
                #Set the indexes that you had set to -1 as 0
                for k in range(0, len(a)):
                    self[a[k]] = 0
            elif(stage == 1):
                #This is a remove stage. Just update your board position according to this
                #Clear the board first
                board = [0] * 31
                for pair in pairs:
                   [weight, position] = pair.split(",")
                   weight = int(weight)
                   position = int(position)
                   board[position + 15] = weight

            
        print("Before Decision")
        print(stage)
        print(board)
        print(self)
        print(opponent)
                 

        #Make a decision
        process = subprocess.Popen(['./arx-prune'], shell = True, stdin = subprocess.PIPE, stdout = subprocess.PIPE)
        process.stdin.write(str(stage))
        process.stdin.write("\n")
        for i in range(0, 31):
            process.stdin.write(str(board[i]) + str(" "))
        process.stdin.write("\n")
        for i in range(0,12):
            process.stdin.write(str(self[i]) + str(" "))
        process.stdin.write("\n")
        for i in range(0,12):
            process.stdin.write(str(opponent[i]) + str(" "))
        process.stdin.write("\n")


    
        #Just read the first line
        output = process.stdout.readline()
        [self_decided_weight, self_decided_position] = output.split(",")
        score = process.stdout.readline()

        #You decided a weight and position
        if(stage == 0):
            #it was a add stage
            lastDecidedWeight = self_decided_weight
            lastDecidedPosition = self_decided_position       
            self[int(self_decided_weight)-1] = 0 #Self No longer has this weight
            board[int(self_decided_position) + 15] = int(self_decided_weight)
        
        print("After Decision")
        print(stage)
        print(board)
        print(self)
        print(opponent)
        print(score)


        #Send it to the server
        s.send(output)
           
            
