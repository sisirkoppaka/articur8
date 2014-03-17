(function ($) {

    function getNewsItems()
    {
        clusterList = JSON.parse(httpGet('/clusters/latest/json/'));
        var clusters = [];
        for(var i = 0; i < clusterList.length; i++){
          var article = clusterList[i].closest_article;
          var short_title = (article.title.length > 100) ? article.title.substr(0, 100).concat(' ...') : article.title;
          clusters.push({index: i+1, title: short_title, url: article.link, text: article.content.substr(0, 200)})
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
        tagName: "article",
        className: "newsItem-container",
        template: $("#newsItemTemplate").html(),

        render: function () {
            var tmpl = _.template(this.template);

            $(this.el).html(tmpl(this.model.toJSON()));
            return this;
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
