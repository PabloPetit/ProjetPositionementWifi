import time
import RPi.GPIO as GPIO

GPIO_TRIGGER = 16
GPIO_ECHO = 18
CALIBRATION_SAMPLE = 20


class Ultra():

	def __init__(self):
		global GPIO_TRIGGER
		global GPIO_ECHO
		self.soundSpeed = 34029 
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(GPIO_TRIGGER,GPIO.OUT) 
		GPIO.setup(GPIO_ECHO,GPIO.IN)
		GPIO.output(GPIO_TRIGGER, False)
		time.sleep(0.5)

	def elapsed_time(self):
		global GPIO_TRIGGER
		global GPIO_ECHO

		GPIO.output(GPIO_TRIGGER, True)
		time.sleep(0.00001)
		GPIO.output(GPIO_TRIGGER, False)

		start = time.time()
		while GPIO.input(GPIO_ECHO)==0:
		  start = time.time()
		while GPIO.input(GPIO_ECHO)==1:
		  stop = time.time()

		elapsed = stop-start

		return elapsed

	def distance(self):
		
		distance = self.elapsed_time() * self.soundSpeed
		distance = distance /2

		return distance

	def calibration(self,dist,show = False):
		# Quand l'algo AVT sera pret, on l'utilisera ici, marche

		global GPIO_TRIGGER
		global GPIO_ECHO
		global CALIBRATION_SAMPLE

		measurements = []

		for i in range(0,CALIBRATION_SAMPLE):
			elapsed = self.elapsed_time() / 2
			time.sleep(0.1)
			if show : 
				print("Time = "+str(elapsed) + "["+str(i)+"]")
			measurements.append(elapsed)

		measurements.remove(min(measurements))
		measurements.remove(max(measurements))

		soundSpeed = 0

		for i in measurements :
			soundSpeed += dist / i

		soundSpeed = soundSpeed / ( CALIBRATION_SAMPLE - 2 )

		if show : 
			print("Sound Speed : "+str(soundSpeed))

		self.soundSpeed = soundSpeed / 2


	def terminate(self):
		GPIO.cleanup()









