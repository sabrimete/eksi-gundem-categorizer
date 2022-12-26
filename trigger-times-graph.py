import matplotlib.pyplot as plt



num_instances = [2, 5, 10]
time_spent = [478.08,189.14,101.0]


plt.scatter(num_instances,time_spent)
plt.xlabel('Max Number Of Instances')
plt.ylabel('Time (s)')
plt.show()

'''

10 request with max instance 3000:
START 2022-12-23 21:15:28.703 EET
END 2022-12-23 21:17:09.542 EET
function_exec_times = [75.022,75.330,75.264,77.586,78.890,81.2156,89.852,94.182,99.593,96.160]
total_time = 101 #seconds

10 request with max instance 5:
Started sending requests at Fri Dec 23 21:50:04 2022
Finished sending requests at Fri Dec 23 21:53:13 2022
Total time: 189.14649081230164
[75.346, 92.965, 93.682, 95.047, 95.083, 161.805, 165.372, 173.146, 184.839, 189.145] 1326.4360406398773

10 request with max instance 2:
Started sending requests at Fri Dec 23 22:07:10 2022
Finished sending requests at Fri Dec 23 22:15:08 2022
Total time: 478.08531308174133
'''