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

  // render: function() {
  //   $.ajax({
  //     method: 'GET',
  //     url: '/electrical/api/trend-unit-1/',
  //     success: function(response) {
  //       response.forEach(function(r) {
  //         var trend1 = new app.RealTimeChartView({
  //           el: '#' + r.tagId,
  //           model: r
  //         });
  //         trend1.render();
  //       });
  //     },
  //     error: function() {}
  //   });
  // }
});

app.trendView = new app.TrendView();
