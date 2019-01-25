# code for dyno testing
# Rebecca McCabe 1-16-19
# Last updated 1-24-19

from time import sleep, ctime
import random, csv
from numpy import arange
import os, sys

dir = os.path.dirname(os.path.abspath(__file__)) + r'\Actuator-Package\Python'
sys.path.append(dir)
from flexseapython.pyFlexsea import *
from flexseapython.pyFlexsea_def import *
from flexseapython.fxUtil import *


labels = ["State time", 					\
"encoder angle", "motor voltage", "torque"	\
]

varsToStream = [ 							\
	FX_STATETIME, 							\
	FX_ENC_ANG,								\
	FX_MOT_VOLT,							\
	FX_GEN_VAR_0							\
]

ENCODER_COUNT_PER_REV = 16384 # 2^14 because 14 bits
CLOCK_COUNT_PER_SEC = 1882 # determined experimentally by comparing STATETIME readings with python datetime

accelThreshold = 3 # rpm / s. Assume equilibrium when acceleration is below this threshold
readingTime = .1   # period in seconds with which to read velocities to detect equilibrium

#motorIds = {'test': 123, 'load': 456}

def setV(motorID, volts):
	mV = volts * 1000
	#setMotorVoltage(motorID, mV)
	print('Passed voltage ', volts, ' to the ', motorID, ' motor.')

def getRPM(motorID):
	angOld = None
	while angOld == None: # wait until it is reading data
		[angOld, timeOld] = fxReadDevice(motorID, [FX_ENC_ANG, FX_STATETIME])
		#print('angOld ',angOld)
		#print('timeOld ',timeOld)
	
	#angOld = random.randint(1,10)
	sleep(readingTime)
	[angNew, timeNew] = fxReadDevice(motorID, [FX_ENC_ANG, FX_STATETIME])
	#print('angNew ',angNew)
	#print('timeNew ',timeNew)
	#angNew = random.randint(1,10)
	deltaRevs = (angNew - angOld) / ENCODER_COUNT_PER_REV
	deltaSeconds = (timeNew - timeOld) / CLOCK_COUNT_PER_SEC
	rpm = deltaRevs / (deltaSeconds/60)
	print('Read rpm ', rpm, ' from the ', motorID, ' motor.')
	return rpm

# def getTorque():
# 	torque = random.random()
# 	print('Read torque ', torque, ' Nm.')
# 	return torque

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
	pass
	# filename = 'dynodata ' + ctime() + '.csv'
	# with open(filename, 'wb') as csvfile:
	# 	filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	# 	filewriter.writerow(labels)
	# 	for row in data:
	# 		filewriter.writerow(row)
	
	# log to csv

#def dynoRun(loadID, testID):
def dynoRun(testID):

	#streamSetup(loadID, testID)
	streamSetup(testID)

	#setControlMode(loadID, CTRL_OPEN)
	setControlMode(testID, CTRL_OPEN)

	print('control mode has been set')

	testVmin = 1
	testVmax = 4.7
	testVstep = .1
	testVs = arange(testVmin, testVmax+testVstep, testVstep)

	loadVmin = 10
	loadVmax = 20
	loadVstep = 5
	loadVs = arange(loadVmin, loadVmax+loadVstep, loadVstep)

	# data = []

	
	#for loadV in loadVs:
	for testV in testVs:
		setV(testID, testV)
		#setV(loadID, loadV)

		accel = 10*accelThreshold # arbitrary high start value	
		rpmOld = getRPM(testID)
		while accel > accelThreshold:			
			sleep(readingTime)
			rpmNew = getRPM(testID)
			accel = abs((rpmNew - rpmOld)/readingTime)
			print('Acceleration: ', accel)
			rpmOld = rpmNew
		print('Equilibrium reached.')	
		
	# 	newData = fxReadDevice(testID, varsToStream)
	# 	printData(labels, newData)
	# 	data = data + newData
	
	print('Turning off control...')
	#setControlMode(loadID, CTRL_NONE)
	setControlMode(testID, CTRL_NONE)		
	sleep(0.2)
	#fxStopStreaming(loadID)
	fxStopStreaming(testID)
	#makeCSV(labels, data)


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
