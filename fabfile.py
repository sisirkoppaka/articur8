from fabric.api import *
from fabric.colors import green, red

import psutil
import re

#Start Motherlode
def start_motherlode(debug='False'):
	if debug:
		local("cd ./articurate/motherlode && node app.js > /dev/null 2>&1 &")
		print green("start_motherlode: Started Motherlode with Debug mode set to "+debug, bold=True)
	else:
		local("cd ./articurate/motherlode && node app.js > ../../motherlode.log 2>&1 &")
		print green("start_motherlode: Started Motherlode with Debug mode set to "+debug, bold=True)


#Stop Motherlode
def stop_motherlode():
	found = 'False';
	for proc in psutil.process_iter():
		try:
			match = re.match(r'.*node.*',proc.name)
			if match:
				print green("stop_motherlode: Found process, stopping "+match.group()+".", bold=True)
				proc.kill()
				found = 'True'
		except:
			continue

	#The below seems to not work, fix me.
	if not found:
		print green("stop_motherlode: Could not find process for Motherlode", bold=True)

def restart_motherlode(debug='False'):
	stop_motherlode()
	start_motherlode(debug)
	print green("restart_motherlode: Finished restarting Motherlode ", bold=True)	

def setup_motherlode():
	local("cd ./articurate/motherlode && npm install")
	print green("setup_motherlode: Finished satisfying prerequisites for Motherlode ", bold=True)

