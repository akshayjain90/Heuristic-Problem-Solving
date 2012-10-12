CC=gcc


all:
	make clean
	make arx-prune
        
arx-prune:
	$(CC) -O2 -Wall config.c approx.c prune.c -o arx-prune

clean:
	rm -f arx-prune
