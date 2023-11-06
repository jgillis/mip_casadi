Linux
```
Architecture:                       x86_64
CPU op-mode(s):                     32-bit, 64-bit
Byte Order:                         Little Endian
Address sizes:                      39 bits physical, 48 bits virtual
CPU(s):                             16
On-line CPU(s) list:                0-15
Thread(s) per core:                 2
Core(s) per socket:                 8
Socket(s):                          1
NUMA node(s):                       1
Vendor ID:                          GenuineIntel
CPU family:                         6
Model:                              141
Model name:                         11th Gen Intel(R) Core(TM) i7-11800H @ 2.30GHz
```


```
fome12

                     1          2           4           8
solver type                                              
gurobi wall   4.184512   1.220026    1.162972    1.049687
       proc   4.183641   2.268364    4.088953    6.881154
cbc    wall  22.074516  22.134662   23.183854   23.561085
       proc  22.720414  22.707247   23.422443   23.762482
highs  wall  26.855823  29.493297   27.950181   25.200284
       proc  26.899460  57.858148  108.273460  193.958909

neos-860300

                     1          2          4           8
solver type                                             
gurobi wall  16.437108  10.574938   3.476326    5.561496
       proc  16.566798  15.935766  11.191620   33.996536
cbc    wall  71.286228  40.231179  27.771119   19.827432
       proc  71.912939  76.268305  95.851644  112.951603
highs  wall   8.320674   8.257809   8.323061    8.785455
       proc   8.841404   8.750790   8.819867    9.323715
```

Columns is amount of threads.

Wall indicates the amount of physical seconds that have elapsed to solve the problem to completion.

Proc indicates the sum of CPU seconds used to solve the problem.
