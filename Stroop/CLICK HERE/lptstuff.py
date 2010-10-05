from VisionEgg.DaqLPT import raw_lpt_module
import time


LPT1 = 0x378 # address of parallel port -- make sure your computer agrees

# turn all pins on
data = 0xFF # values to output on parallel port
raw_lpt_module.out(LPT1,data)


#time.sleep(5.0) # wait 1 second

for i in range(5000):
	input_value = raw_lpt_module.inp(0x378) & 0x10
	print input_value
	time.sleep(0.001)

# turn all pins off
#data = 0x00
#raw_lpt_module.out(LPT1,data)
