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


app.RealTimeChartContainerView = Backbone.View.extend({
  initialize: function(props) {
  
  }
});

app.RealTimeChartView = Backbone.View.extend({
  template: _.template($('#realtime-chart-container-template').html()),

  initialize: function(props) {
    this.props = props;
    this.el = props.el;

    // pagination
    this.state = { historical: true, first: false, start: 0, rows: 60 };
  },

  events: {
    'click .btn-historical': 'toggleTrend',
    'click .btn-pagination': 'paginate',
  },

  toggleTrend: function() {
    console.log('toggle historical');
  },

  paginate: function(e) {
    var tagId = $(e.currentTarget).parent().parent().next().attr('id');
    if (tagId === this.model.tagId) {
      // paginationType: [ first | prev | next | last ]
      var paginationType = $(e.currentTarget).text();
      if (paginationType === 'First') {
        this.state.first = true;
        this.state.start = 0;
      }

      if (paginationType === 'Last') {
        this.state.first = false;
        this.state.start = 0;
      }

      if (paginationType === 'Prev' && this.state.first === false) {
        this.state.start += this.state.rows;
      }

      if (paginationType === 'Prev' && this.state.first === true) {
        this.state.start -= this.state.rows;
      }

      if (paginationType === 'Next' && this.state.first === false) {
        this.state.start -= this.state.rows;
      }

      if (paginationType === 'Next' && this.state.first === true) {
        this.state.start += this.state.rows;
      }

      var data = {
        page: this.model.page,
        eq: this.model.tagId,
        start: this.state.start,
        rows: this.state.rows,
        first: this.state.first
      };

      var that = this;
      $.ajax({
        method: 'get',
        url: '/electrical/api/historical-trend/',
        data: data,
        success: function(response) {
          that.model = response[0];
          that.model.page = data.page;
          $('#' + that.model.tagId).empty();
          that.modifySeries();
          that.renderHighchart();
          that.updateButton($(e.currentTarget));
        }
      });
    }
  },

  updateButton: function(el) {
    if (el === undefined) { return; }

    var btnGroup = el.parent();
    var btnFirst = btnGroup.children().eq(0);
    var btnPrev = btnGroup.children().eq(1);
    var btnNext = btnGroup.children().eq(2);
    var btnLast = btnGroup.children().eq(3);

    if (this.state.first === false && this.state.start === 0) {
      btnFirst.prop('disabled', false);
      btnPrev.prop('disabled', false);
      btnNext.prop('disabled', true);
      btnLast.prop('disabled', true);
    }
  
    if (this.state.first === true && this.state.start === 0) {
      btnFirst.prop('disabled', true);
      btnPrev.prop('disabled', true);
      btnNext.prop('disabled', false);
      btnLast.prop('disabled', false);
    }

    if (this.state.first === false && this.state.start !== 0) {
      btnFirst.prop('disabled', false);
      btnPrev.prop('disabled', false);
      btnNext.prop('disabled', false);
      btnLast.prop('disabled', false);
    }

    if (this.state.first === true && this.state.start !== 0) {
      btnFirst.prop('disabled', false);
      btnPrev.prop('disabled', false);
      btnNext.prop('disabled', false);
      btnLast.prop('disabled', false);
    }
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

    console.log(this.model);
    this.$el.append(this.template(this.model));
    this.renderHighchart();
  },

  renderHighchart: function() {
    $('#' + this.model.tagId).highcharts({
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

app.FileBrowserView = Backbone.View.extend({
  initialize: function() {
    this.homeDir = this.model.data.path;
    this.currDir = this.model.data.path;
  },

  template: _.template($('#file-browser-template').html()),

  events: {
    'click #file-browser-home-btn': 'handleHome',
    'click #file-browser-back-btn': 'handleBack',
    'click .file-browser-folder': 'handleFolder'
  },

  handleHome: function() {
    $('#file-browser-table').empty();
    this.currDir = this.homeDir;
    var data = {path: this.homeDir};
    this.getDir(this.model.url, data);
    this.updateCurrentDir();
  },

  handleBack: function() {
    if (this.currDir === this.homeDir) { return; }

    $('#file-browser-table').empty();
    this.currDir = this.currDir.substring(0, this.currDir.lastIndexOf('/'));
    var data = {path: this.currDir};
    this.getDir(this.model.url, data);
    this.updateCurrentDir();
  },

  handleFolder: function(e) {
    $('#file-browser-table').empty();
    this.currDir = this.currDir + '/' + $(e.currentTarget).text();
    var data = {path: this.currDir};
    this.getDir(this.model.url, data);
    this.updateCurrentDir();
  },

  updateCurrentDir: function() {
    $('#file-browser-current-dir').text(this.currDir);
  },

  render: function() {
    this.$el.append(this.template());
    this.getDir(this.model.url, this.model.data);
    this.updateCurrentDir();
  },

  modifyDirAsLink: function(data) {
    if (data === undefined) {return};
    var that = this;
    data.forEach(function(d) {
      if (d.type === 'folder') {
        d.Name = '<a href="#" class="file-browser-folder">' + d.Name + '</a>';
      }

      if (d.type === 'file') {
        d.Name = '<a href="' + that.model.url + 'download/' + '?path=' + that.currDir + '/' + d.Name + '">' + d.Name + '</a>';
      }
    });
    return data;
  },

  getDir: function(url, data) {
    var that = this;

    var spinner = new Spinner().spin();
    $('#file-browser-table').append(spinner.el);

    YUI().use(
      'aui-datatable',
      'datatable-scroll',
      function(Y) {
        $.ajax({
          url: url,
          data: data,
          method: 'GET',
          // seconds
          // timeout: 30000,
          success: function(response) {
            // remove spinner
            $('#file-browser-table').empty();

            if (response.success === -1) {
              $('#file-browser-table').append('<p>' + response.error_message + '</p>');
              return;
            }

            var columns = [{key: 'Name', allowHTML: true}];
            var data = that.modifyDirAsLink(response);
    
            new Y.DataTable({
              columns: columns,
              data: data,
              scrollable: 'y',
              height: '400px'
            })
              // .Base({ columnset: columns, recordset: data })
            .render('#file-browser-table');
          },
          error: function(response) {
            $('#file-browser-table').empty();
            if (response.statusText === 'timeout') {
              $('#file-browser-table').append('<p style="margin:0">Timeout</p>');
              $('#file-browser-table').append(response.statusText);
            }
          }
        });
      }
    );
  }
});
