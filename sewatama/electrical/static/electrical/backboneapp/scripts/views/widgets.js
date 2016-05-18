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

  render: function() {
    Highcharts.setOptions({
      global : { useUTC : false }
    });

    this.$el.highcharts({
      title: { text: this.model.title },
      subtitle: { text: this.model.subtitle },
      plotOptions: { line: { marker: { enabled: false } } },
      tooltip: { shared: true },
      exporting: { enabled: false },
      credits: false,
      chart : {
        events : {
          load : function () {
            // set up the updating of the chart each second
            var series = this.series[0];
            var series2 = this.series[1];
            var series3 = this.series[2];
            setInterval(function () {
              var x = (new Date()).getTime();

              var y = getRandomInt(0, 250);
              series.addPoint([x, y], true, true);

              y = getRandomInt(0, 1500);
              series2.addPoint([x, y], true, true);

              y = Math.round(Math.random() * 40);
              series3.addPoint([x, y], true, true);
            }, 1000);
          }
        }
      },
      xAxis: [
          // set x-axis label in datetime format
        { type: 'datetime',
          tickmarkPlacement: 'on',
          // set grid
          gridLineWidth: 1 }
      ],
      yAxis: [
        { max: 40,
          tickInterval: 8,
          labels: {
            format: '{value}°C',
            style: { color: Highcharts.getOptions().colors[2] }
          },
          title: {
            text: 'Temperature',
            style: { color: Highcharts.getOptions().colors[2] }
          },
          opposite: true },
        { max: 250,
          tickInterval: 50,
          title: {
            text: 'Rainfall',
            style: { color: Highcharts.getOptions().colors[0] }
          },
          labels: {
            format: '{value} mm',
            style: { color: Highcharts.getOptions().colors[0] }
          },
          opposite: true },
        { max: 1500,
          tickInterval: 300,
          title: {
            text: 'Sea-Level Pressure',
            style: { color: Highcharts.getOptions().colors[1] }
          },
          labels: {
            format: '{value} mb',
            style: { color: Highcharts.getOptions().colors[1] }
          },
          opposite: true }
      ],
      series: [
        { name: 'Rainfall',
          yAxis: 1,
          data: (function() {
            var i = 0;
            var time = (new Date()).getTime();
            var x = [49.9, 71.5, 106.4, 129.2, 144.0, 176.0, 135.6, 148.5, 216.4, 194.1, 95.6, 54.4];
            var data = [];

            x.forEach(function(d) {
                data.push([time + i * 1000, d]);
                i = i + 1;
            });

            return data;
          }()),
          tooltip: { valueSuffix: ' mm' } }, 
        { name: 'Sea-Level Pressure',
          yAxis: 2,
          data: (function() {
            var i = 0;
            var time = (new Date()).getTime();
            var x = [1016, 1016, 1015.9, 1015.5, 1012.3, 1009.5, 1009.6, 1010.2, 1013.1, 1016.9, 1018.2, 1016.7];
            var data = [];

            x.forEach(function(d) {
                data.push([time + i * 1000, d]);
                i = i + 1;
            });

            return data;
          }()),
          tooltip: { valueSuffix: ' mb' } },
        { name: 'Temperature',
          data: (function() {
            var i = 0;
            var time = (new Date()).getTime();
            var x = [7.0, 6.9, 9.5, 14.5, 18.2, 21.5, 25.2, 26.5, 23.3, 18.3, 13.9, 9.6];
            var data = [];

            x.forEach(function(d) {
                data.push([time + i * 1000, d]);
                i = i + 1;
            });

            return data;
          }()),
          tooltip: { valueSuffix: ' °C' } }
      ]
    });
  }
});
