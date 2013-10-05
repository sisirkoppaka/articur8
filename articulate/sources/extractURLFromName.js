var jsdom = require('jsdom')
  , querystring = require('querystring')
  , util = require('util')
  , cheerio = require('cheerio')
  , request = require('request')
  , fs = require('fs')
  , readline = require('readline')
  , csv = require('csv');

process.setMaxListeners(0);

var fileName = "univ_list.csv";

/*csv()
.from.path(
  fileName)
.to.array( function(data){
  /*for (var i=0; i<data.length; i++) {
  console.log(data[i].toString());
 };*/
/*for (var i = 0; i < data.length; i++) {
  sleep(1000);

  var URL = 'http://www.google.com/search?hl=en&q=%s&start=%s&sa=N&num=%s&ie=UTF-8&oe=UTF-8';
    var resultsPerPage = 10;
    var start = 0;
    var query = data[i].toString();//line;//'Harvard University';
    var newURL = util.format(URL, querystring.escape(query), start, resultsPerPage);

console.log(newURL + "\n");

var options = {
  url: newURL,
  qs: { },
  headers: { 'user-agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11' }
};

request(options, function (err, res, body) {
  var $ = cheerio.load(body);
  //console.log('hello',$('body').html());
  //request.setMaxListeners(0);
  console.log(' ',$('h3.r').first().children().attr('href'));
} );
};*/


function sleep(milliseconds) {
  var start = new Date().getTime();
  for (var i = 0; i < 1e7; i++) {
    if ((new Date().getTime() - start) > milliseconds){
      break;
    }
  }
}





var read = readline.createInterface({
    input: fs.createReadStream(fileName),
    output: process.stdout,
    terminal: false
});

read.on('line',function(line) {

    //if asynchronous then paste here, but it crashes EventListeners

      //sleep(10);

  var URL = 'http://www.google.com/search?hl=en&q=%s&start=%s&sa=N&num=%s&ie=UTF-8&oe=UTF-8';
    var resultsPerPage = 10;
    var start = 0;
    var query = line;//data[i].toString();//line;//'Harvard University';
    var newURL = util.format(URL, querystring.escape(query), start, resultsPerPage);

console.log(newURL + "\n");

var options = {
  url: newURL,
  qs: { },
  headers: { 'user-agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11' }
};

request(options, function (err, res, body) {
  var $ = cheerio.load(body);
  //console.log('hello',$('body').html());
  //request.setMaxListeners(0);
  console.log(' ',$('h3.r').first().children().attr('href'));
} );
//});

/*jsdom.env({
  html: "http://www.google.com/search?hl=en&q=Harvard%20University&start=0&sa=N&num=10&ie=UTF-8&oe=UTF-8",
  headers: 
  'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',

  scripts: [
    'http://code.jquery.com/jquery.js'
  ],
  done: function(errors, window) {
    var $ = window.$;
    //console.log(' ',$('h3.r').first().children().attr('href');
    console.log('hello',$('body').text());
  }
});*/
});

