var app = app || {};

app.Widget = Backbone.Model.extend({});
app.WidgetList = Backbone.Collection.extend({ model: app.Widget });


app.GaugeView = Backbone.View.extend({
  template: _.template($('#gauge-template').html()),
  render: function() {
    this.$el.html(this.template(this.model.toJSON()));
    return this;
  },

  bindGauge: function(params) {
    new JustGage({
      id: params.tagId,
      min: params.minValue,
      max: params.maxValue,
      value : Math.round(params.value * 100) / 100,
      label: params.label,
      decimals: 2,
      gaugeWidthScale: 0.5,
      counter: true,
      formatNumber: true
    });
  }
});


app.OneColumnTableView = Backbone.View.extend({
  template: _.template($('#onecolumn-table-template').html()),

  render: function() {
    // title that has two words will be rendered in two lines
    if (typeof this.model.title !== 'undefined') {
      this.model.title = this.model.title.replace(' ', '<br/>');
    }

    // render template
    this.$el.append(this.template(this.model));

    // render rows inside tbody
    var that = this;
    this.model.data.forEach(function(item) {
      var itemView = new app.OneColumnTableItemView({
        el: $('#' + that.model.tagId),
        model: item
      }); 
      itemView.render();
    });
  }
});


app.OneColumnTableItemView = Backbone.View.extend({
  template: _.template($('#onecolumn-table-item-template').html()),

  render: function() {
    this.$el.append(this.template(this.model));
  }
});


app.ThreeColumnsTableView = Backbone.View.extend({
  template: _.template($('#threecolumns-table-template').html()),

  render: function() {
    // render template
    this.$el.append(this.template(this.model));

    // render rows inside tbody
    var that = this;
    this.model.data.forEach(function(item) {
      var itemView = new app.ThreeColumnsTableItemView({
        el: $('#' + that.model.tagId),
        model: item
      }); 
      itemView.render();
    });
  }
});


app.ThreeColumnsTableItemView = Backbone.View.extend({
  template: _.template($('#threecolumns-table-item-template').html()),

  render: function() {
    this.$el.append(this.template(this.model));
  }
});


app.ImageView = Backbone.View.extend({
  template: _.template($('#image-template').html()),

  render: function() {
    this.$el.append(this.template(this.model));
  }
});
