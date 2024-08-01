from tfs.profiler.timer import Timer
from tfs.profiler.stack import Stack
import time
t1 =Timer().start(1)
for i in range(5):
    t2 = Timer().start(2)
    time.sleep(1)
    if i == 3:
        for j in range(i):
            t3 = Timer().start(3)
            time.sleep(1)
            t3.end()
    t2.end()
t1.end()
t1.print("test_output")

