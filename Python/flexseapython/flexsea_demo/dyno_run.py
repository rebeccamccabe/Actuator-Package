# code for dyno testing
# Rebecca McCabe 1-16-19
# Last updated 1-25-19

from time import sleep, ctime
import random, csv
import numpy as np
import os, sys

dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(dir)
from flexseapython.pyFlexsea import *
from flexseapython.pyFlexsea_def import *
from flexseapython.fxUtil import *

###################### TEST PARAMETERS ##########################################

deltaRpmThreshold = 10 # expected delta rpm from reading to reading with no acceleration. Assume equilibrium when the delta rpm is below this threshold.
readingTime = .05   # period in seconds with which to read velocities to detect equilibrium. If this is too small, the code will presume that the deltaRpm is due to noise when it really is due to acceleration. 

testVmin = 1
testVmax = 4.6
testVstep = .2
testVs = np.arange(testVmin, testVmax+testVstep, testVstep)

loadVmin = 1
loadVmax = 2
loadVstep = 1
loadVs = np.arange(loadVmin, loadVmax+loadVstep, loadVstep)

################### DATA STREAM PARAMETERS ######################################

labels = ["torque", "testVmeas", "time", "encVelocity", "encAngle"]

varsToStream = [ 							\
	FX_GEN_VAR_0,							\
	FX_MOT_VOLT,							\
	FX_STATETIME,							\
	FX_ENC_VEL,								\
	FX_ENC_ANG								\
]

ENCODER_COUNT_PER_REV = 16384 # 2^14 because 14 bits
CLOCK_COUNT_PER_SEC = 1882 # determined experimentally by comparing STATETIME readings with python datetime

dataNames = ["testV", "loadV", "myRpm", "theirRpm", "torque", "testVmeas", "time"] #TODO: eventually add temp and current
numDataPts = len(testVs)*len(loadVs)
data = np.zeros((len(dataNames),numDataPts))


######################## FUNCTIONS #################################################

def setV(motorID, volts):
	mV = volts * 1000
	#setMotorVoltage(motorID, mV)
	print('Passed voltage ', volts, ' to the ', motorID, ' motor.')

def getRPM(motorID):
	angOld = None
	while angOld == None: # wait until it is reading data
		[angOld, timeOld] = fxReadDevice(motorID, [FX_ENC_ANG, FX_STATETIME])
	
	sleep(readingTime)
	[angNew, timeNew] = fxReadDevice(motorID, [FX_ENC_ANG, FX_STATETIME])
	
	deltaRevs = (angNew - angOld) / ENCODER_COUNT_PER_REV
	deltaSeconds = (timeNew - timeOld) / CLOCK_COUNT_PER_SEC
	rpm = deltaRevs / (deltaSeconds/60)
	print('Read rpm ', rpm, ' from the ', motorID, ' motor.')
	return rpm

#def streamSetup(loadID, testID):
def streamSetup(testID):
	#fxSetStreamVariables(loadID, varsToStream)
	fxSetStreamVariables(testID, varsToStream)

	#streamSuccess0 = fxStartStreaming(loadID, 100, False, 0)
	streamSuccess1 = fxStartStreaming(testID, 100, False, 0)

	#if(not (streamSuccess0 and streamSuccess1)):
	if(not (streamSuccess1)):
		print("streaming failed...")
		sys.exit(-1)

def makeCSV(labels, data):
	timestamp = ctime().replace(" ","_").replace(":","_")
	filename = "dynoCSVs/dynodata_" + timestamp + ".csv"

	print('csv labels ', labels)

	with open(filename, 'w') as csvfile:
		filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
		filewriter.writerow(labels)
		for i in range(data.shape[1]):
			filewriter.writerow(data[:,i])

#def dynoRun(loadID, testID):
def dynoRun(testID):

	#streamSetup(loadID, testID)
	streamSetup(testID)

	#setControlMode(loadID, CTRL_OPEN)
	setControlMode(testID, CTRL_OPEN)

	print('control mode has been set')

	counter=0
	for loadV in loadVs:
		for testV in testVs:
			setV(testID, testV)

			#setV(loadID, loadV)
			print('pretending to set loadV ', loadV)

			deltaRpm = 10*deltaRpmThreshold # arbitrary high start value	
			rpmOld = getRPM(testID)
			while deltaRpm > deltaRpmThreshold:			
				sleep(readingTime)
				rpmNew = getRPM(testID)
				deltaRpm = abs(rpmNew - rpmOld)
				print('deltaRpm: ', deltaRpm)
				rpmOld = rpmNew
			print('Equilibrium reached.\n')	

			[torque, testVmeas, time, encVel, encAng] = fxReadDevice(testID, varsToStream)
			print('got data')
			data[:,counter] = [testV, loadV, rpmNew, encVel, torque, testVmeas, time]
			counter+=1
	
	print(dataNames)
	makeCSV(dataNames, data)
	
	print('Turning off control...')
	#setControlMode(loadID, CTRL_NONE)
	setControlMode(testID, CTRL_NONE)		
	sleep(0.2)
	#fxStopStreaming(loadID)
	fxStopStreaming(testID)


if __name__ == '__main__':
	#ports = sys.argv[1:3]
	ports = sys.argv[1:2]
	devIds = loadAndGetDevice(ports)
	try:
		#dynoRun(devIds[0], devIds[1])
		dynoRun(devIds[0])
	except Exception as e:
		print("broke: " + str(e))
		pass
