#!/usr/bin/python

from flask import Flask, render_template, jsonify, abort, request

from reaver_toolkit import AiroDump

import sys

app = Flask(__name__)
airodump = AiroDump()

@app.route('/')
def home():
	return render_template('index.html')

@app.route('/list')
def list():
	results = []
	for network_id in airodump.networks:
		result = {}
		network = airodump.networks[network_id]
		result['encryption'] = network[1]
		result['network_id'] = network_id
		result['bssid'] = network_id
		result['channel'] = network[0]
		result['quality'] = network[4]
		result['essid'] = network[5]
		result['known'] = False
		results.append(result)

	return jsonify(data = results)

@app.route('/scan')
def scan():
	airodump.refresh_networks()
	return list()

@app.route('/connect/<int:network_id>')
def connect(network_id):
	is_valid_wireless_network_id(network_id)

	wireless.ConnectWireless(network_id)

	return jsonify(data = wireless.GetWirelessProperty(network_id, 'essid'))

@app.route('/details/<int:network_id>')
def details(network_id):
	is_valid_wireless_network_id(network_id)

	result = {}
	result['encryption'] = 'Off'
	if wireless.GetWirelessProperty(network_id, 'encryption'):
		result['encryption'] = wireless.GetWirelessProperty(network_id, 'encryption_method')

	result['network_id'] = network_id
	result['bssid'] = wireless.GetWirelessProperty(network_id, 'bssid')
	result['channel'] = wireless.GetWirelessProperty(network_id, 'channel')
	result['quality'] = wireless.GetWirelessProperty(network_id, 'quality')
	result['essid'] = wireless.GetWirelessProperty(network_id, 'essid')
	if result['essid'] == '<hidden>' : result['essid'] = ''

	# check if there's key/passphrase stored (WPA1/2 and WEP only, sorry)
	result['known'] = (wireless.GetWirelessProperty(network_id, 'key') or wireless.GetWirelessProperty(network_id, 'apsk') or wireless.GetWirelessProperty(network_id, 'passphrase') or False) and True

	return jsonify(data = result)

@app.route('/config', methods=['POST'])
def config():
	'''
	0	wpa                 	WPA 1/2 (Hex [0-9/A-F])
  	Req: key (Key)
	---
	2	wpa-psk             	WPA 1/2 (Passphrase)
	  Req: apsk (Preshared Key)
	---
	5	wep-hex             	WEP (Hex [0-9/A-F])
	  Req: key (Key)
	---
	6	wep-passphrase      	WEP (Passphrase)
	  Req: passphrase (Passphrase)
	'''
	if not request.json:
		abort(400)

	try:
		network_id = int(request.json.get('networkid', None))
	except:
		network_id = -1

	is_valid_wireless_network_id(network_id)

	for property, value in request.json.iteritems():
		if property.startswith('wicd-'):
			pp = property[5:]
			wireless.SetWirelessProperty(network_id, pp, value)

	passkey = request.json.get('passkey', None)

	if passkey:
		enctype = request.json.get('wicd-enctype', None)
		enckey = None
		
		if enctype in [ 'wpa', 'wep-hex']:
			enckey = 'key'
		elif enctype == 'wpa-psk':
			enckey = 'apsk'
		elif enctype == 'wep-passphrase':
			enckey = 'passphrase'

		if enckey:
			wireless.SetWirelessProperty(network_id, enckey, passkey)


	result = {}
	return jsonify(data = result)

@app.route('/status')
def status():
	check = wireless.CheckIfWirelessConnecting()
	status = wireless.CheckWirelessConnectingStatus()
	message = wireless.CheckWirelessConnectingMessage()

	return jsonify(data = (check, status, message))

@app.route('/disconnect')
def disconnect():
	daemon.Disconnect()

	return jsonify(data = None)

@app.route('/current')
def current():

	ip = wireless.GetWirelessIP("")
	result = {}

	if ip:
		result['ip'] = ip
		if daemon.NeedsExternalCalls():
			iwconfig = wireless.GetIwconfig()
		else:
			iwconfig = ''
		result['network'] = wireless.GetCurrentNetwork(iwconfig)

		if daemon.GetSignalDisplayType() == 0:
			result['quality'] = wireless.GetCurrentSignalStrength(iwconfig)
		else:
			result['quality'] = wireless.GetCurrentDBMStrength(iwconfig)

	return jsonify(data = result)

if __name__ == "__main__":
	app.run(host='0.0.0.0')
