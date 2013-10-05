var jsdom = require('jsdom')
  , querystring = require('querystring')
  , util = require('util')
  , cheerio = require('cheerio')
  , request = require('request')
  , fs = require('fs')
  , readline = require('readline')
  , csv = require('csv')
  , redis = require('redis')
  , client = redis.createClient("6379","127.0.0.1");

//Connect to Redis

client.on("error", function (err) {
  console.log("Error " + err);
});

//client.set("blush","value");

  var URL = 'http://www.mit.edu';
    /*var resultsPerPage = 10;
    var start = 0;
    var query = line;//data[i].toString();//line;//'Harvard University';
    var newURL = util.format(URL, querystring.escape(query), start, resultsPerPage);
*/
var newURL = URL;

//console.log(newURL + "\n");

var feeds = new Array();
feeds.push("temp");

function sleep(milliseconds) {
  var start = new Date().getTime();
  for (var i = 0; i < 1e7; i++) {
    if ((new Date().getTime() - start) > milliseconds){
      break;
    }
  }
}

var options = {
  url: newURL,
  qs: { },
  headers: { 'user-agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11' }
};

request(options, function (err, res, body) {
  var $ = cheerio.load(body);
  console.log(' ',$("[type='application/rss+xml']").attr('title'));
  console.log(' ',$("[type='application/rss+xml']").attr('href'),'\n');
  //client.incr("feeds");
  var feedURL = $("[type='application/rss+xml']").attr('href');
  feeds.push(feedURL);
  console.log(feedURL);

  sendToRedis(feedURL);
  //client.set("feed:1",feedURL);
  client.quit();

} );
  //console.log(feeds[0]);

function sendToRedis(feedURL) {
  client.set("feed:1",feedURL,redis.print);
    client.set("ark","vark",redis.print);

};


//client.quit();

