var app = app || {};

app.DashboardView = Backbone.View.extend({
  initialize: function() {
    app.widgets = new app.WidgetList();
    app.widgets.url = '/electrical/api/sld-outgoing-1/';

    // TODO synchronous xmlhttprequest is BAD
    app.widgets.fetch({ async: false });
    this.render();

    var that = this;
    setInterval(function() {
      app.widgets.fetch({ async: false });
      $('.gridster > ul').empty();
      that.render();
    }, 20000);
  },

  render: function() {
    app.widgets.each(function(widget) {
      if (widget.get('type') === 'image') {
        var widgetView = new app.ImageView({
          el: $('#grid-0 > ul'),
          model: widget.toJSON()
        });
        widgetView.render();
      }

      if (widget.get('type') === 'oneColumnTable') {
        var widgetView = new app.OneColumnTableView({
          el: $('#grid-1 > ul'),
          model: widget.toJSON()
        });
        widgetView.render();
      }

      if (widget.get('type') === 'threeColumnsTable') {
        var widgetView = new app.ThreeColumnsTableView({
          el: $('#grid-2 > ul'),
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
    widget_base_dimensions: [90, 30],
    min_cols: 12,
    max_cols: 12,
    max_size_x: 12})
  .data('gridster')
  .disable();

gridster[1] = $("#grid-1 ul")
  .gridster({
    namespace: '#grid-1',
    widget_margins: [5, 5],
    widget_base_dimensions: [90, 30],
    min_cols: 12,
    max_cols: 12,
    max_size_x: 12})
  .data('gridster')
  .disable();

gridster[2] = $("#grid-2 ul")
  .gridster({
    namespace: '#grid-2',
    widget_margins: [5, 5],
    widget_base_dimensions: [110, 19],
    min_cols: 12,
    max_cols: 12,
    max_size_x: 12})
  .data('gridster')
  .disable();
