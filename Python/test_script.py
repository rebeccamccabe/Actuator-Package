import os, sys, datetime
thisdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(thisdir)

from flexseapython.pyFlexsea import *
from flexseapython.pyFlexsea_def import *
from flexseapython.fxUtil import *

# experiment controls two devices with open voltage commands

# device 1: 
# 			starts at 0 mV
#			ramps up to MAX_V (mV) in RAMP_TIME (seconds)
#			holds while other device does delta ramp/short hold
#			holds MAX_V for LONG_HOLD_TIME (seconds)
#			holds while other device does delta ramp/short hold
#			ramps down to 0 in RAMP_TIME (seconds)

# device 2: 
# 			starts at 0 mV 
#			ramps to negative MAX_V (mV) in RAMP_TIME (seconds) 					// initial ramp
#			holds negative MAX_V for SHORT_HOLD_TIME (seconds)  					// short hold
#			ramps to negative MAX_V + DELTA_V (mv) in DELTA_RAMP_TIME (seconds) 	// delta ramp
# 			holds for LONG_HOLD_TIME (seconds) 										// long hold
#			ramps back to negative MAX_V in DELTA_RAMP_TIME 						// delta ramp
# 			holds for SHORT_HOLD_TIME 												// short hold
# 			ramps to 0 in RAMP_TIME 												// final ramp

COM_PORTS_OF_DEVICES = ['COM3', 'COM9']
MAX_V = 5000.0
RAMP_TIME = 3.0

SHORT_HOLD_TIME = 0.5
LONG_HOLD_TIME = 10.0
DELTA_V = 1000.0
DELTA_RAMP_TIME = 1.0

# print( -1 * MAX_V + DELTA_V )
# print(HOLD_TIME - 2 * (SHORT_HOLD_TIME + DELTA_RAMP_TIME))

STREAM_FREQ = 500

labels = [									\
"State time", "encoder angle", 				\
"motor voltage", "motor current"			\
]

varsToStream = [ 							\
	FX_STATETIME, FX_ENC_ANG,				\
	FX_MOT_VOLT, FX_MOT_CURR				\
]

starttime = 0
def busySleepUntil(t):
	while(datetime.datetime.now())

def experiment(devId0, devId1):

	# configure streams...
	fxSetStreamVariables(devId0, varsToStream)
	fxSetStreamVariables(devId1, varsToStream)

	# start streams...
	# streaming over wire at 500Hz is no problem
	# using auto streaming to avoid clogging the pipeline
	# logging just for fun
	streamSuccess0 = fxStartStreaming(devId0, STREAM_FREQ, True, 1)
	streamSuccess1 = fxStartStreaming(devId1, STREAM_FREQ, True, 1)

	setControlMode(devId0, CTRL_OPEN)
	setControlMode(devId1, CTRL_OPEN)
	setMotorVoltage(devId0, 0)
	setMotorVoltage(devId1, 0)

	dt = 1.0 / STREAM_FREQ
	numsteps = (int)(RAMP_TIME / dt)
	dV = MAX_V / numsteps

	print("Starting experiment")
	# printing in the loops below will throw off timings
	# as is timings in python are bad

	print(datetime.datetime.now())

	# initial ramp up stage
	for i in range(0, numsteps):
		setVoltage = dV * (i+1)
		setMotorVoltage(devId0, setVoltage)
		setMotorVoltage(devId1, -setVoltage)
		sleep(dt)

	print(datetime.datetime.now())

	# short hold stage
	sleep(SHORT_HOLD_TIME)

	numsteps = (int)(DELTA_RAMP_TIME / dt)
	dV = DELTA_V / numsteps

	# delta ramp stage
	for i in range(0, numsteps):
		setVoltage = -1 * MAX_V + (i + 1) * dV
		setMotorVoltage(devId1, setVoltage)
		sleep(dt)

	# both holding stage
	sleep( LONG_HOLD_TIME )

	# reverse delta ramp stage
	for i in range(0, numsteps):
		setVoltage = -1 * MAX_V + (numsteps - i - 1) * dV
		setMotorVoltage(devId1, setVoltage)
		sleep(dt)

	# short hold stage
	sleep(SHORT_HOLD_TIME)

	numsteps = (int)(RAMP_TIME / dt)
	dV = MAX_V / numsteps

	print(datetime.datetime.now())

	# final ramp down stage
	for i in range(0, numsteps):
		setVoltage = MAX_V - dV * (i+1)
		setMotorVoltage(devId0, setVoltage)
		setMotorVoltage(devId1, -setVoltage)
		sleep(dt)


	print(datetime.datetime.now())
	
	# clean up
	setMotorVoltage(devId0, 0)
	setMotorVoltage(devId1, 0)
	setControlMode(devId0, CTRL_NONE)
	setControlMode(devId1, CTRL_NONE)

	# sleep so that previous commands go through before we stop streaming
	sleep(0.2)
	fxStopStreaming(devId0)
	fxStopStreaming(devId1)

def main():

	devIds = loadAndGetDevice(COM_PORTS_OF_DEVICES)
	devIds = sorted(devIds)
	print('Got devices: ' + str(devIds))

	try:
		experiment(devIds[0], devIds[1])
	except Exception as e:
		print("broke: " + str(e))
		pass

main()
