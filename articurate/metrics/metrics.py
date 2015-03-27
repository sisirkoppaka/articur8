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

#Use as @metrics.track_by("key") to store return value of the function in motherlode, indexed by key.
#This allows one to store multiple return values of a function at once.
#Do not use any other decorators below this, just as with @metrics.track
#It is recommended not to use trailing _ in the function name which is encapsulated by this decorator.
#Will still work, but it's easier for me to debug stuff this way. And it's not likely either that
#a trailing _ will be needed.
def track_by(key):
	def track(f):
		def newfn(*args, **kwargs):
			out = f(*args, **kwargs)
			shortmethodName = f.__module__+"."+f.__name__
			methodName = f.__module__+"."+f.__name__+"_"+key
			api.storeMetric(methodName, out)
			print blue("metrics.track:")+cyan(shortmethodName)+"_"+magenta(key)
			return out
		return newfn
	return track 