Sample commands to run server and opposing clients:

./nanomunchers.exe server -data-file ./data/data1.txt -num-nanomunchers 5 -port 8000 -time-delay 1 -protocol-log-file-team-1 team1_messages.txt -protocol-log-file-team-2 team2_messages.txt

./nanomunchers.exe client -num-nanomunchers 5 -port 8000 -team-name Team1


python main.py <no-nanomunchers> <port> <teamname> : Make sure Python version is 2.7 or higher 
  
