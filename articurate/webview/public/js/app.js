(function ($) {

    function createCookie(name,value,days) {
    	  if (days) {
    		    var date = new Date();
    		    date.setTime(date.getTime()+(days*24*60*60*1000));
    		    var expires = "; expires="+date.toGMTString();
    	  }
    	  else var expires = "";
    	  document.cookie = name+"="+value+expires+"; path=/";
    }

    function readCookie(name) {

        var nameEQ = name + "=";
        var ca = document.cookie.split(';');

        for(var i = 0; i < ca.length; i++) {
      		var c = ca[i];
      		while (c.charAt(0)==' ') c = c.substring(1,c.length);
      		if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    	  }

        return "";
    }

    function eraseCookie(name) {
    	 createCookie(name,"",-1);
    }

    function makeDict(a)
    {
        var dictionary = {};
        for(var i=0;i<a.length;i++)
        {
            dictionary[a[i]]='';
        }
        return dictionary;
    }

    function getNewsItems()
    {
        var readList = makeDict(readCookie('articurateCookie').split(','));

        clusterList = JSON.parse(httpGet('/clusters/latest/json/'));
        var clusters = [];
        for(var i = 0; i < clusterList.length; i++){
          var article = clusterList[i].closest_article;
          var hash = clusterList[i].hash;
          var num_articles = clusterList[i].articles.length;
          var short_title = (article.title.length > 100) ? article.title.substr(0, 100).concat(' ...') : article.title;
          var unread = "background: rgba(11,211,24,0.5);border-color: rgba(11,211,24,0.6);";
          var read = "background: rgba(255,19,0,0.5);border-color: rgba(255,19,0,0.6);";
          var color = unread;
          if(hash in readList) {color = read;}
          clusters.push({color: color, index: i+1, hash: hash, title: short_title, url: article.link, num_articles: num_articles, text: article.content.substr(0, 200)})
        }
        return clusters;
    }

    function httpGet(theUrl)
    {
        var xmlHttp = null;

        xmlHttp = new XMLHttpRequest();
        xmlHttp.open( "GET", theUrl, false );
        xmlHttp.send( null );
        return xmlHttp.response;
    }

    //define news item model
    var NewsItem = Backbone.Model.extend();

    //define collection of all news
    var AllNews = Backbone.Collection.extend({
        model: NewsItem
    });

    //define individual news item view
    var NewsItemView = Backbone.View.extend({
        tagName: "li",
        className: "table-view-cell",
        template: $("#newsItemTemplate").html(),

        render: function () {
            var tmpl = _.template(this.template);

            $(this.el).html(tmpl(this.model.toJSON()));
            return this;
        },

        //add ui events
        events: {
            "click .table-view-cell": "makeRed"
        },

        //change color of indicator
        makeRed: function (e) {
            this;
            this.$el.find("#indicator").css("background", "rgba(255,19,0,0.5)");
            this.$el.find("#indicator").css("border-color", "rgba(255,19,0,0.6)");

            // cookie time
            var current_cookie = readCookie('articurateCookie');

            // shorten cookie if needed
            var cookie_list = current_cookie.split(',');
            var threshold = 200;
            if(cookie_list.length == threshold){
                var short_cookie = cookie_list[1];
                for(var i = 2; i < threshold; i++){
                  short_cookie = short_cookie + ',' + cookie_list[i];
                }
                current_cookie = short_cookie;
            }

            // extend the readList
            if(current_cookie.length == 0)
                new_cookie = $(e.currentTarget).attr('id');
            else
                new_cookie = current_cookie + ',' + $(e.currentTarget).attr('id');

            createCookie('articurateCookie', new_cookie, 1);
        }

    });

    //define master view
    var AllNewsView = Backbone.View.extend({
        el: $("#news"),

        initialize: function () {
            this.collection = new AllNews(getNewsItems());
            this.render();
        },

        render: function () {
            var that = this;
            _.each(this.collection.models, function (item) {
                that.renderNewsItem(item);
            }, this);
        },

        renderNewsItem: function (item) {
            var itemView = new NewsItemView({
                model: item
            });
            this.$el.append(itemView.render().el);
        }
    });

    //create instance of master view
    var news = new AllNewsView();

} (jQuery));
