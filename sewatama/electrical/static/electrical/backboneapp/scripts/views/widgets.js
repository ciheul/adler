var app = app || {};


function getRandomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}


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


app.RealTimeChartView = Backbone.View.extend({
  initialize: function(props) {
    this.props = props;
    this.el = props.el;
  },

  modifySeries: function() {
    if (this.model.series === undefined) {
      return;
    }

    this.model.series.forEach(function(s) {
      s.data = s.data.map(function(d) {
        return [(new Date(d[0]).getTime()), d[1]];
      });
    });
  },

  render: function() {
    // Highcharts.setOptions({
    //   global : { useUTC : false }
    // });

    this.modifySeries();

    this.$el.highcharts({
      title: { text: this.model.title },
      subtitle: { text: this.model.subtitle },
      plotOptions: { line: { marker: { enabled: false } } },
      tooltip: { shared: true },
      exporting: { enabled: false },
      credits: false,
      // chart: {
      //   events: {
      //     load: function() {
      //       var that = this;
      //       setInterval(function() {
      //         for (var i = 0; i < that.series.length; i++) {
      //           var s = that.series[i];
      //           console.log(i);
      //           // TODO ajax to query the latest row
      //           $.ajax({
      //             method: 'get',
      //             url: '/electrical/api/trend-unit-1/cylinder-exhause-temperature/?id=' + i,
      //             success: function(response) {
      //               console.log(response);
      //               var x = (new Date()).getTime();
      //               var y = getRandomInt(1020, 1100);
      //
      //               var graph = s.graph;
      //               var area = s.area;
      //               var currentShift = (graph && graph.shift) || 0;
      //
      //               Highcharts.each([graph, area, s.graphNeg, s.areaNeg],
      //                 function(shape) {
      //                   if (shape) { shape.shift = currentShift + 1; }
      //                 });
      //
      //               s.data[0].remove(false, false);
      //
      //               s.addPoint([(new Date(response[0])).getTime(), response[1]]);
      //               // s.addPoint([x, y]);
      //               console.log(s.data.length);
      //             }
      //           });
      //         }
      //       }, 10000);
      //     }
      //   }
      // },
      xAxis: [
          // set x-axis label in datetime format
        { type: 'datetime',
          // tickmarkPlacement: 'on',
          // set grid
          gridLineWidth: 1 }
      ],
      yAxis: this.model.yAxis,
      series: this.model.series
    });
  }
});
