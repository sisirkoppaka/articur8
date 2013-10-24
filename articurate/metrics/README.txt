GUIDE TO USING METRICS
======================

The Metrics subsystem allows tracking of various points of our entire system. Points are defined by the return values of any function. If you can make what you want to track into a separate function, Metrics will track the latest output of that function call. Metrics also lets you retrieve tracked objects. Tracking and Retrieving are discussed below.

GUIDE TO TRACKING
-----------------

Tracking is done internally via Motherlode by backing up to Redis. Let's say you have a function as follows:

def foo():
	xyz
	...
	return bar
end

In order to track 'bar', add the following to the line above the function def,

@metrics.track
def foo():
	xyz
	...
	return bar
end

We also need to import the Metrics module in the first place. That can be done by adding the following import statement,

from articurate.metrics import metrics

@metrics.track
def foo():
	xyz
	...
	return bar
end

That's it. Metrics is now tracking 'bar'. 

This does not change the behavior of foo(). If you call foo() anywhere else, you will still get a return value of bar.

Metrics is designed to track the latest return values at various points in Articurate by injecting itself into the call tree and doing a sideway store to Redis via Motherlode (internally). Note the word 'latest'. So, don't use this for functions that are called repeatedly (say for each article, in a given run of clusterer). Instead write a small encapsulating function that collects the return values for all articles and then do the above tracking on that function. 

That's all you need to do for tracking _any object_, _anywhere_ in Articurate.

GUIDE TO RETRIEVING
-------------------

To retrieve, you need to tell Metrics what you would like to retrieve. Metrics uses the function address in the module space as keys for objects to be tracked. This means that if the above function foo was in articurate/clustering/clusterer.py, then foo's key is articurate.clustering.clusterer.foo - as simple as that!

Retrieval is supported via PyMotherlode (Python API to Motherlode). To retrieve bar now, anywhere else in Articurate, first do the following import in that file,

from articurate.pymotherlode import api

Then, do,

object = api.getMetric("articurate.clustering.clusterer.foo")

'object' should now equal 'bar'.


OTHER INFORMATION
-----------------

This information is just for those interested. 
-Internal encoding of all objects in Metrics is via JSON using the jsonpickle module. 

More will be added as Metrics changes.
