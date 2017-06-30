
import sys
sys.path.append("/home/pi/Adafruit-Raspberry-Pi-Python-Code/Adafruit_PWM_Servo_Driver")

from Adafruit_PWM_Servo_Driver import PWM
import pifacerelayplus as PFRP
import os

import time
import threading
import atexit


class Strobe(threading.Thread):
	def __init__(self,parent,pindex,rindex,ontime,offtime):
		super(Strobe,self).__init__()
		self.parent = parent
		self.pindex = pindex
		self.rindex = rindex
		self.ontime = ontime
		self.offtime = offtime
		self.relay = self.parent.pfr[pindex].relays[rindex]

	def run(self):
		while self.relay.strobeThread != False:
			self.relay.turn_on()
			time.sleep(self.ontime)
			self.relay.turn_off()
			time.sleep(self.offtime)

class Dalek:
	
	PFR_EYE = 0
	PFR_DOME_LIGHTS = 0
	PFR_RIFLE = 0
	PFR_TORCH = 0
	PFR_INPUT = 0
	
	RELAY_EYE = 0
	RELAY_DOME_LIGHTS = 1
	RELAY_RIFLE = 2
	RELAY_TORCH = 3

	INPUT_DOME_SWITCH = 2
	INTERRUPT_DOME_SWITCH = 6
	SETTLE_DOME_SWITCH = .1
	
	PWM_IRIS = 0
	
	SERVO_IRIS = 2

	STROBE_DOME_DEFAULT_ON_TIME = .01
	STROBE_DOME_DEFAULT_OFF_TIME = .1
	STROBE_TORCH_DEFAULT_ON_TIME = .02
	STROBE_TORCH_DEFAULT_OFF_TIME = .02

	SERVO_RATE_IRIS_MIN = 115
	SERVO_RATE_IRIS_MAX = 350
	SERVO_RATE_IRIS_DEFAULT = SERVO_RATE_IRIS_MIN
	SERVO_RATE_IRIS_SPAN = SERVO_RATE_IRIS_MAX - SERVO_RATE_IRIS_MIN
	SERVO_RATE_IRIS_RATIO = SERVO_RATE_IRIS_SPAN / 100
	SERVO_STEP_IRIS = 1
	SERVO_DELAY_IRIS = .005
	SERVO_CRUISE_IRIS = .5

	SPEAK_DELAY_SYLLABLE = .1
	SPEAK_DELAY_WORD = .3
	SPEAK_DELAY_SENTENCE = 1

	SPEAK_AMPLITUDE_DEFAULT = 80
	SPEAK_PITCH_DEFAULT = 90
	SPEAK_SPEED_DEFAULT = 150

	SPEAK_AMPLITUDE_UP = 100
	SPEAK_PITCH_UP = 100
	SPEAK_SPEED_UP = 80

	SPEAK_AMPLITUDE_DOWN = 90
	SPEAK_PITCH_DOWN = 80
	SPEAK_SPEED_DOWN = 100

	def __init__(self):
		self.initializeRelays()
		self.initializeServos()
		self.initializeInterrupts()
		atexit.register(self.cleanup)

	def initializeRelays(self):
		self.pfr = []
		self.pfr.append( PFRP.PiFaceRelayPlus() )
		self.clearRelays()

	def initializeServos(self):
		self.pwm = []
		pwm = PWM(0x40)
		pwm.setPWMFreq(50)
		self.pwm.append(pwm)
		self.clearServos()
		pwm.setPWM(Dalek.SERVO_IRIS, 0, Dalek.SERVO_RATE_IRIS_DEFAULT)
		self.irisCurrentRate = Dalek.SERVO_RATE_IRIS_DEFAULT
		self.servoWait( Dalek.PWM_IRIS, Dalek.SERVO_IRIS, Dalek.SERVO_CRUISE_IRIS )
		

	def initializeInterrupts(self):
		self.listener = PFRP.InputEventListener(chip=self.pfr[Dalek.PFR_INPUT])
		self.listener.register(Dalek.INTERRUPT_DOME_SWITCH, PFRP.IODIR_BOTH, 
			self.toggleDomeLights, settle_time = Dalek.SETTLE_DOME_SWITCH)
		self.listener.activate()

	def clearRelays(self):
		for pfr in self.pfr:
			for relay in pfr.relays:
				relay.turn_off()

	def clearServos(self):
		for pwm in self.pwm:
			for servo in range(0,15):
				pwm.setPWM(servo,4096,0)

	def clearStrobes(self):
		for pfr in self.pfr:
			for relay in pfr.relays:
				self.endStrobe(relay)

	def clearInterrupts(self):
		self.listener.deactivate()

	def cleanup(self):
		self.clearInterrupts()
		self.clearStrobes()
		self.clearRelays()
		self.clearServos()

	def endStrobe(self,relay):
		if not hasattr(relay,"strobeThread"):
			return
		strobeThread = relay.strobeThread
		if strobeThread != False:
			relay.strobeThread = False
			strobeThread.join()

	def servoWait( self, pindex, sindex, cruiseTime ):
		time.sleep(cruiseTime)
		self.pwm[pindex].setPWM(sindex, 4096, 0)

	def setIrisServo( self, target ):
		if target == "open":
			percent = 100
		elif target == "close":
			percent = 0
		else:
			percent = int(target)
		if percent < 0 or percent > 100:
			return False
		percent = 100 - percent
		targetRate = int(Dalek.SERVO_RATE_IRIS_MIN + percent * Dalek.SERVO_RATE_IRIS_RATIO)
		increment = 1 if targetRate > self.irisCurrentRate else -1
		pwm = self.pwm[Dalek.PWM_IRIS]
		while abs(self.irisCurrentRate - targetRate) > Dalek.SERVO_STEP_IRIS:
			self.irisCurrentRate += increment * Dalek.SERVO_STEP_IRIS
			pwm.setPWM(Dalek.SERVO_IRIS, 0, self.irisCurrentRate)
			time.sleep(Dalek.SERVO_DELAY_IRIS)
		self.irisCurrentRate = targetRate
		pwm.setPWM(Dalek.SERVO_IRIS, 0, targetRate)
		self.servoWait(Dalek.PWM_IRIS, Dalek.SERVO_IRIS, Dalek.SERVO_CRUISE_IRIS)
		return True


	def setRelay(self, pindex, rindex, val):
		pfr = self.pfr[pindex].relays[rindex].value = val

	def toggleDomeLights(self,event):
		self.setRelay(Dalek.PFR_DOME_LIGHTS, Dalek.RELAY_DOME_LIGHTS, event.direction == 0)

	def speak(self, dialog):
		sentences = dialog.split(".")
		sentenceDelay = 0
		for sentence in sentences:
			time.sleep(sentenceDelay)
			sentenceDelay = Dalek.SPEAK_DELAY_SENTENCE
			words = sentence.split(" ")
			wordDelay = 0
			for word in words:
				time.sleep(wordDelay)
				wordDelay = Dalek.SPEAK_DELAY_WORD
				syllables = word.split("-")
				syllableDelay = 0
				for syllable in syllables:
					if syllable and not syllable.isspace():
						time.sleep(syllableDelay)
						syllableDelay = Dalek.SPEAK_DELAY_SYLLABLE
						if syllable[:1] == ">":
							syllable = syllable[1:]
							pitch = Dalek.SPEAK_PITCH_UP
							speed = Dalek.SPEAK_SPEED_UP
							amplitude = Dalek.SPEAK_AMPLITUDE_UP
						elif syllable[:1] == "<":
							syllable = syllable[1:]
							pitch = Dalek.SPEAK_PITCH_DOWN
							speed = Dalek.SPEAK_SPEED_DOWN
							amplitude = Dalek.SPEAK_AMPLITUDE_DOWN
						else:
							pitch = Dalek.SPEAK_PITCH_DEFAULT
							speed = Dalek.SPEAK_SPEED_DEFAULT
							amplitude = Dalek.SPEAK_AMPLITUDE_DEFAULT
						cmd = "espeak -v en-rp '%s' -p %s -s %s -a %s -z 2>/dev/null" % (syllable, pitch, speed, amplitude)
						self.doCommand("dome on")
						os.system(cmd)
						self.doCommand("dome off")



	def doStrobe(self,words):
		if words[1] == "dome":
			pindex = Dalek.PFR_DOME_LIGHTS
			rindex = Dalek.RELAY_DOME_LIGHTS
			ontime = Dalek.STROBE_DOME_DEFAULT_ON_TIME
			offtime = Dalek.STROBE_DOME_DEFAULT_OFF_TIME
		elif words[1] == "torch":
			pindex = Dalek.PFR_TORCH
			rindex = Dalek.RELAY_TORCH
			ontime = Dalek.STROBE_TORCH_DEFAULT_ON_TIME
			offtime = Dalek.STROBE_TORCH_DEFAULT_OFF_TIME
		elif words[1] == "off":
			self.clearStrobes()
			return True
		else:
			return False
		relay = self.pfr[pindex].relays[rindex]
		if len(words) > 2:
			if words[2] == "off":
				self.endStrobe(relay)
				return True
			offtime = float(words[2])
		if len(words) > 3:
			ontime = float(words[3])
		self.endStrobe(relay)
		strobeThread = Strobe(self,pindex,rindex,ontime,offtime)
		relay.strobeThread = strobeThread
		strobeThread.start()
		return True

	def doCommand(self, command):
		words = command.split(" ")
		if words[0] == "exit":
			self.clearInterrupts()
			exit()
		elif words[0] == "relay":
			pfr = int(words[1])
			relay = int(words[2])
			val = words[3] == "on"
			self.setRelay(pfr,relay,val)
			return
		elif words[0] == "eye":
			val = words[1] == "on"
			self.setRelay( Dalek.PFR_EYE, Dalek.RELAY_EYE, val )
			return
		elif words[0] == "dome":
			val = words[1] == "on"
			self.setRelay( Dalek.PFR_DOME_LIGHTS, Dalek.RELAY_DOME_LIGHTS, val )
			return
		elif words[0] == "torch":
			val = words[1] == "on"
			self.setRelay( Dalek.PFR_TORCH, Dalek.RELAY_TORCH, val )
			return
		elif words[0] == "rifle":
			val = words[1] == "on"
			self.setRelay( Dalek.PFR_RIFLE, Dalek.RELAY_RIFLE, val )
			return
		elif words[0] == "strobe":
			if ( self.doStrobe(words) ):
				return
		elif words[0] == "input":
			for xpin in self.pfr[0].x_pins:
				print( "pin:", xpin.value )
			return
		elif words[0] == "iris":
			if self.setIrisServo( words[1] ):
				return
		elif words[0] == "say":
			self.speak( command[4:] )
			return
		elif words[0] == "fire":
			self.doCommand("rifle on")
			self.doCommand("strobe torch")
			self.speak("ex-ter-min >ate. ex-ter-min >ate")
			self.doCommand("strobe torch off")
			self.doCommand("rifle off")
			return
		elif words[0] == "spew":
			self.speak("you are the <doc tor. you are an en-ah-me of the <dah leks. you will be ex <ter min-ate >ted.")
			return
		elif words[0] == "reset":
			self.clearStrobes()
			self.clearRelays()
			self.clearServos()
			return
		print('command ', command, ' not found')


