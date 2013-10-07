"""Metrics: Methods to store and access system state"""
from fabric.colors import green, magenta,cyan,blue
from articurate.pymotherlode import api

#Use as @metrics.inspect to print return value in terminal 
def inspect(f):
	def newfn(*args, **kwargs):
		out = f(*args, **kwargs)
		#print blue("metrics.inspect:")+cyan(f.__module__+"."+f.__name__+":")+green(str(out))
		print blue("metrics.inspect:")+green(str(out))
		return out
	return newfn

#Use as @metrics.track to store return value in the motherlode, do not use any other decorators below this
def track(f):
	def newfn(*args, **kwargs):
		out = f(*args, **kwargs)
		methodName = f.__module__+"."+f.__name__
		api.storeMetric(methodName, out)
		print blue("metrics.track:")+cyan(methodName)
		return out
	return newfn