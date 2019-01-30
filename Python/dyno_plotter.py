# read the dyno csv data and generate relevant graphs
# Rebecca McCabe
# 1-28-19

import numpy as np
import scipy
import matplotlib.pyplot as plt
from matplotlib import cm
import csv

file = 'dynoCSVs//dynodata_Fri_Jan_25_16_53_41_2019.csv'

############## import the csv file ##########################
testV = []
loadV = []
myRPM = []
theirRPM = []
torque = []
testVmeas = []
time = []
#TODO - make these numpy arrays instead of python lists

with open(file, 'rt') as csvfile:
	reader = csv.reader(csvfile, delimiter=',', quotechar='|')
	next(reader) # no data is in the first row so skip it
	for row in reader:
		if len(row) > 0:
			testV.append(float(row[0]))
			loadV.append(float(row[1]))
			myRPM.append(float(row[2]))
			theirRPM.append(float(row[3]))
			torque.append(float(row[4]))
			testVmeas.append(float(row[5]))
			time.append(float(row[6]))

# print('testV ', testV)
# print('loadV ', loadV)
# print('myRPM ', myRPM)
# print('theirRPM ', theirRPM)
# print('torque ', torque)
# print('testVmeas ', testVmeas)
# print('time ', time)


################## make graphs ######################

# no load speed vs voltage
plt.figure(1)
#TODO: plot only data points where there's no torque 
plt.scatter(testV, myRPM, label='my RPM')
plt.scatter(testV, theirRPM, label='their RPM')
plt.xlabel('Voltage commanded to the test motor (V)')
plt.ylabel('No-Load Speed (RPM)')
plt.legend()


# torque speed curve
plt.figure(2)
uniqueVoltages, idxs = np.unique(testV, return_inverse=True)
normVs = uniqueVoltages / max(uniqueVoltages)
colors = [ cm.jet(x) for x in normVs ]
for v, uniqueVoltage in enumerate(uniqueVoltages):
	idxsOfUniqueV = [i for i, e in enumerate(testV) if e == uniqueVoltage]
	rpmsAtThisV = [myRPM[i] for i in idxsOfUniqueV]
	torquesAtThisV = [torque[i] for i in idxsOfUniqueV]
	plt.scatter(rpmsAtThisV, torquesAtThisV, color=colors[v], label='voltage='+ str(round(uniqueVoltage,2)))
plt.xlabel('Speed (RPM)')
plt.ylabel('Torque (Nm)') 
plt.legend()

plt.show()
