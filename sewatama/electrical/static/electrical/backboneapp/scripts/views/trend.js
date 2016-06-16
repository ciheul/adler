var app = app || {};

app.TrendView = Backbone.View.extend({
  initialize: function() {
    app.widgets = new app.WidgetList();
    app.widgets.url = '/electrical/api/trend-unit-1/';

    // TODO synchronous xmlhttprequest is BAD
    app.widgets.fetch({ async: false });
    this.render();
  },

  render: function() {
    app.widgets.each(function(widget) {
      console.log(widget.toJSON());
      var widgetView = new app.RealTimeChartView({
        el: $('#grid-0 > ul'),
        model: widget.toJSON()
      });
      widgetView.render();
    });
  },
});

app.trendView = new app.TrendView();
