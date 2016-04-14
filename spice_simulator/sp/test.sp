* mosfet off A w o-  v1 v2 td tf pw per
* Vin 1 0 0 sin 1.5 1.5 80M 0
Vin 2 0 1	pulse 0 3 0 0 50n 60n
R1 2 1 1k
C1 1 0 1p




*.DC  Vin 0 3 0.1
.tran TR 0 40n 10p
.END



* mosfet off A w o-
* Vin 1 0 0 sin 1.5 1.5 80M 0
Vin 2 0 1	pulse 0 3 5n 5n 20n 40n
Cc 2 1 1p
Cb 1 0 1p
Rd 1 0 1k



*.DC  Vin 0 3 0.1
.tran TR 0 200n 10p
.END