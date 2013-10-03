var express = require('express');
var app = express()
  , redis = require('redis')
  , client = redis.createClient("6379","127.0.0.1");;

app.use(express.limit('15mb'));
app.use(express.bodyParser());

//GET /
app.get('/', function(req,res) {
	res.type('text/plain');
	res.send('I am gestating. Have some patience till the due date.');
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

app.listen(process.env.PORT || 9999);

