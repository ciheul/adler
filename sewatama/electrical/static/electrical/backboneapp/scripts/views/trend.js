var app = app || {};


app.TrendView = Backbone.View.extend({
  initialize: function() {
    this.render();
  },

  render: function() {
    // var model = {
    //   title: 'G1T101 - CYLINDER EXHAUSE TEMPERATURE',
    // };

    $.ajax({
      method: 'GET',
      url: '/electrical/api/trend-unit-1/',
      success: function(response) {
        console.log(response);
        response.forEach(function(r) {
          var trend1 = new app.RealTimeChartView({
            el: '#' + r.tagId,
            model: r
          });
          trend1.render();
        });
      },
      error: function() {}
    });

  }
});

app.trendView = new app.TrendView();
