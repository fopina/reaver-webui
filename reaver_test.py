from reaver_toolkit import AiroDump, Wash
import time

def airodump_test():
	a = AiroDump()
	a.refresh_networks()
	print a.networks

def wash_test():
	w = Wash()
	w.start()
	for i in xrange(10):
		time.sleep(1)
		print w.networks

if __name__ == '__main__':
	#airodump_test()
	wash_test()