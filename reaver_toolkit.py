import pexpect
import time
import os
import threading

class AiroDump(object):
	def __init__(self, interface = 'mon0'):
		self.networks = {}
		self.interface = interface

	def refresh_networks(self, timeout = 3, fileprefix = 'dump'):
		self.networks = {}
		dump = pexpect.spawn('airodump-ng %s -w %s --output-format csv -a' % (self.interface, fileprefix))
		time.sleep(timeout)
		dump.close()

		filename = '%s-01.csv' % fileprefix
		dump_file = open(filename, 'r')

		for line in dump_file:
			if line.startswith('BSSID,') or line == '\r\n':
				continue
			elif line.startswith('Station'):
				break
			else:
				words = line.split(',')
				# BSSID, First time seen, Last time seen, channel, Speed, Privacy, Cipher, Authentication, Power, # beacons, # IV, LAN IP, ID-length, ESSID, Key
				self.networks[words[0]] = (
					words[3].strip(),	# channel
					words[5].strip(),	# Privacy
					words[6].strip(),	# Cipher
					words[7].strip(),	# Authentication
					words[8].strip(),	# Power
					words[13],			# ESSID
					)
		
		os.remove(filename)

class Wash(object):

	def __init__(self, interface = 'mon0'):
		self.networks = {}
		self.interface = interface
		self._thread = None

	def start(self):
		if self._thread:
			return
		self._thread = threading.Thread(target = self.thread_run)
		self._thread.start()

	def stop(self):
		self._thread.stop()
		self._thread = None

	def thread_run(self):
		for i in xrange(100):
			self.networks[i] = 1
			print i