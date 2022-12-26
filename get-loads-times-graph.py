import matplotlib.pyplot as plt



single_times = [21.223137140274048,69.55752086639404,138.57977199554443,138.04651999473572,137.55237817764282,140.47146320343018,139.59927439689636,138.73570728302002,138.31584000587463,138.5709729194641]
load_balanced_times = [26.087740898132324,60.502968072891235,16.01768183708191,15.641102075576782,16.76445198059082,16.127695083618164,15.824057817459106,17.008074283599854,16.078509092330933,16.054347038269043]

plt.ion()
fig, ax = plt.subplots()
plt.plot(single_times, label='Single Machine')
plt.plot(load_balanced_times, label='Load Balanced')
plt.xlabel('Request (per 5000)')
plt.ylabel('Time (s)')
plt.title('Responding 50k Requests | Load Balanced vs Single Machine')
plt.figtext(.6, .6, f"Total Times: \nSingle Machine: {round(sum(single_times),2)}s \nLoad Balanced: {round(sum(load_balanced_times),2)}s")
ax.annotate('The point where auto scaling happens', xy=(1,load_balanced_times[1]), xycoords='data',
            xytext=(100,60), textcoords='offset points',
            arrowprops=dict(arrowstyle='fancy',fc='0.6'))
plt.legend()
plt.show()
plt.pause(20)