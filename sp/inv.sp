* mosfet off A w o-
* Vin 1 0 0 sin 1.5 1.5 80M 0
Vin 2 0 0	pulse 3 0 0 0 20n 30n
Vdd 1 0 3
C1 4 0 1p
MP2 4 2 1 4 1
MN4 4 2 0  2 1
*R1 4 0 20k


.DC  Vin 0 3 0.01
*.tran TR 0 100n 10p
.END
Vin 1 0 1	
Vdd 2 0 3
C1 3 0 1p
MP2 3 1 2 40 1
MN1 3 1 0 20 1

C2 5 0 10p
MP3 5 3 2 40 1
MN4 5 3 0 20 1

C3 7 0 10p
MP5 7 5 2 40 1
MN6 7 5 0 20 1



C4 8 0 10p
MP7 8 7 2 40 1
MN8 8 7 0 20 1

C5 8 0 10p
MP9 7 9 2 40 1
MN10 7 9 0 20 1
.tran TR 0 100n 10p
.END
* R1 3 2 100k
* R1 3 2 100k
* .DC  Vin 0 3 0.1
.tran TR 0 100n 10p
.END
