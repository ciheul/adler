var app = app || {};

app.DashboardView = Backbone.View.extend({
  initialize: function() {
    app.widgets = new app.WidgetList();
    app.widgets.url = '/electrical/api/report-sfc-outgoing/';

    // TODO synchronous xmlhttprequest is BAD
    app.widgets.fetch({ async: false });
    this.render();

    var that = this;
    setInterval(function() {
      app.widgets.fetch({ async: false });
      $('.gridster > ul').empty();
      that.render();

      $('.page-notif').fadeIn();
      $('.page-notif').delay(3000).fadeOut();
    }, app.constants.DATA_UPDATE_INTERVAL);
  },

  render: function() {
    app.widgets.each(function(widget) {
      if (widget.get('type') === 'threeColumnsTable') {
        var widgetView = new app.ThreeColumnsTableView({
          el: $('#grid-0 > ul'),
          model: widget.toJSON()
        });
        widgetView.render();
      }
    });
  }
});

app.dashboardView = new app.DashboardView();


var gridster = [];

gridster[0] = $("#grid-0 ul")
  .gridster({
    namespace: '#grid-0',
    widget_margins: [5, 5],
    widget_base_dimensions: [90, 23],
    min_cols: 12,
    max_cols: 12,
    max_size_x: 12})
  .data('gridster')
  .disable();
