var app = app || {};


app.TrendView = Backbone.View.extend({
  initialize: function() {
    this.render();
  },

  render: function() {
    var model = {
      title: 'G1T101 - CYLINDER EXHAUSE TEMPERATURE',
    };

    trend1 = new app.RealTimeChartView({
      el: '#container',
      model: model
    });
    trend1.render();
  }
});

app.trendView = new app.TrendView();
