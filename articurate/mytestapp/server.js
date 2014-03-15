var express = require('express');
var app = express()
  , redis = require('redis')
  , client = redis.createClient("6379","127.0.0.1")
  , stylus = require('stylus')
  , nib = require('nib')
  , us = require('underscore')
  , ratchet = require('ratchet')
  , backbone = require('backbone')
  , jq = require('jquery')
  , js = require('JSON2');


app.use(express.logger('dev'))
app.use(express.bodyParser({limit: '500mb'}));

function compile(str, path) {
	return stylus(str)
		.set('filename', path)
		.use(nib())
}

app.set('views', __dirname + '/views')
//app.set('view engine', 'jade')
app.use(stylus.middleware(
{
	src: __dirname + '/public'
	, compile: compile
}));
app.use(express.static(__dirname + '/public'))


app.get('/clusters/latest/', function (req, res) {
  	client.get("clusters:latest",function(err,value){
		res.type('text/html');
		res.render('index',
 		 { title : 'articulate',
 		   clusterJSON : value 
 		 });
		//console.log(value);
		//res.send(value);
	});
});

app.get('/demo', function(req,res) {
  res.sendfile('index.html');
});

//GET /
app.get('/', function(req,res) {
	res.type('text/plain');
	res.send('I am gestating.');
});

//GET /dumps/delta/latest
app.get('/dumps/delta/latest',function(req,res) {

	client.get("dumps:delta:latest",function(err,timestamp) {
		client.get("dumps:delta:"+timestamp,function(err,value){
			res.type('text/xml');
			res.send(value);
		});	
	});
});

//GET /dumps/delta/:timestamp
app.get('/dumps/delta/:timestamp',function(req,res) {
	client.get("dumps:delta:"+req.params.timestamp,function(err,value){
		res.type('text/xml');
		console.log(value);
		res.send(value);
	});
});

//POST /dumps/delta
app.post('/dumps/delta/',function(req,res) {
	if(!req.body.hasOwnProperty('timestamp') || 
 	   !req.body.hasOwnProperty('deltadump')) {
		res.statusCode = 400;
		return res.send('Error 400: Deltadumping API incorrect.');
	}

	client.set(("dumps:delta:"+req.body.timestamp),req.body.deltadump);
	client.set("dumps:delta:latest",req.body.timestamp);
	client.rpush("dumps:delta:sorted",req.body.timestamp);
	res.json(true);
});

//POST /dumps/delta
app.post('/metrics/track/',function(req,res) {
	if(!req.body.hasOwnProperty('method') || 
 	   !req.body.hasOwnProperty('methodPayload')) {
		res.statusCode = 400;
		return res.send('Error 400: Deltadumping API incorrect.');
	}

	client.set(("metrics:track:"+req.body.method),req.body.methodPayload);
	//client.set("metrics:track:latest",req.body.timestamp);
	client.sadd("metrics:track:set",req.body.method);
	res.json(true);
});

//GET /dumps/delta/:timestamp
app.get('/metrics/track/:method',function(req,res) {
	client.get("metrics:track:"+req.params.method,function(err,value){
		res.type('text/x-json');
		console.log(value);
		res.send(value);
	});
});

app.post('/clusters/latest/',function(req,res) {
	if(!req.body.hasOwnProperty('clusterInJSON') || 
 	   !req.body.hasOwnProperty('tag')) {
		res.statusCode = 400;
		return res.send('Error 400: Latest Cluster Saving API incorrect.');
	}
	client.set("clusters:latest",req.body.clusterInJSON);
	res.json(true);
});

//GET /clusters/latest
app.get('/clusters/latest/json/',function(req,res) {
	client.get("clusters:latest",function(err,value){
		res.type('application/json');
		//console.log(value);
		res.send(value);
	});
});

app.listen(process.env.PORT || 9999);

