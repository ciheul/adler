var app = app || {};

app.DashboardView = Backbone.View.extend({
  initialize: function() {
    app.widgets = new app.WidgetList();
    app.widgets.url = '/electrical/api/genset-overview-outgoing-1/';

    // TODO synchronous xmlhttprequest is BAD
    app.widgets.fetch({ async: false });

    this.render();
  },

  render: function() {
    app.widgets.each(function(widget) {
      if (widget.get('type') === 'threeColumnsTable') {
        console.log(widget);
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
