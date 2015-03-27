var express = require('express');
var app = express()
  , redis = require('redis')
  , client = redis.createClient("6379","127.0.0.1")
  , stylus = require('stylus')
  , nib = require('nib')
  , us = require('underscore');


app.use(express.logger('dev'))
app.use(express.bodyParser({limit: '500mb'}));

function compile(str, path) {
	return stylus(str)
		.set('filename', path)
		.use(nib())
}

//app.set('views', __dirname + '/views')
//app.set('view engine', 'jade')

app.use(stylus.middleware(
{
  src: __dirname + '/public',
	compile: compile
}));
app.use(express.static(__dirname + '/public'))

/*
app.get('/clusters/latest/', function (req, res) {
  	client.get("clusters:latest",function(err,value){
		res.type('text/html');
		res.render('index',
 		 { title : 'articulate',
 		   clusterJSON : value
 		 });
	});
});
*/

//GET /
app.get('/', function(req,res) {
	res.type('text/plain');
	res.send('I am gestating.');
});

app.listen(process.env.PORT || 9999);
