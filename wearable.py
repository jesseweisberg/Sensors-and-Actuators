import os
import glob
import RPi.GPIO as GPIO
import time

age = input('What is your age?')
if (age < 20):
  BPM_limit = 120
elif (age > 20 & age < 50):
  BPM_limit = 100
else:
  BPM_limit = 80

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

GPIO.setmode(GPIO.BCM)

def read_temp_raw():
  f = open(device_file, 'r')
  lines = f.readlines()
  f.close()
  return lines

def read_temp():
  lines = read_temp_raw()
  while lines[0].strip()[-3:] != 'YES':
    time.sleep(0.2)
    lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
  if equals_pos != -1:
    temp_string = lines[1][equals_pos+2:]
    temp_c = float(temp_string) / 1000.0
    temp_f = temp_c * 9.0 / 5.0 + 32.0  
    motor=16
    GPIO.setup(motor,GPIO.OUT)
  if temp_f>80: 
    GPIO.output(motor, GPIO.HIGH)
  else :
    GPIO.output(motor, GPIO.LOW)
  return temp_c, temp_f


def readadc(adcnum, clockpin, mosipin, misopin, cspin):
  if ( (adcnum > 7) or (adcnum < 0) ):
    return -1
  GPIO.output(cspin, True)

  GPIO.output(clockpin, False)
  GPIO.output(cspin, False)

  commandout = adcnum
  commandout |= 0x18
  commandout <<=3
  for i in range(5):
    if (commandout & 0x80):
      GPIO.output(mosipin, True)
    else:
      GPIO.output(mosipin, False)
    commandout <<=1
    GPIO.output(clockpin, True)
    GPIO.output(clockpin, False)

  adcout = 0
  
  for i in range(12):
    GPIO.output(clockpin, True)
    GPIO.output(clockpin, False)
    adcout <<= 1
    if (GPIO.input(misopin)):
      adcout |= 0x1

  GPIO.output(cspin, True)

  adcout >>= 1
  return adcout

SPICLK = 18
SPIMISO = 23
SPIMOSI = 24
SPICS = 25

GPIO.setwarnings(False)

GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)
GPIO.setup(17,GPIO.OUT)
GPIO.setup(21,GPIO.OUT)

pulse_adc = 0

THRESH = 512

pulse = False
countBeats=0
countTime=0
runTime =0

while True:
 analog_value = readadc(pulse_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
 for i in range(analog_value / 100):
  print ".",

 if (analog_value > THRESH):
  if (pulse == False):
   pulse = True
   print "Beat"
   countBeats+=1
   GPIO.output(17,GPIO.HIGH)
   
  else:
   print ""
 
 else:
  pulse = False
  print ""

 time.sleep(0.1)
 GPIO.output(17,GPIO.LOW)
 countTime+=1

 if (countTime==100):
  BPM= 6*countBeats
  print "BPM = " + str(BPM)
  print(read_temp())
  runTime+=1
  if (BPM>BPM_limit):
   GPIO.output(21,GPIO.HIGH)
  else:
   GPIO.output(21,GPIO.LOW)
  countTime=0
  countBeats=0
 if (runTime == 5):
  GPIO.output(16,GPIO.LOW)
  GPIO.cleanup()

