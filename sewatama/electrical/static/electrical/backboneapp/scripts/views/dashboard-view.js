var app = app || {};

(function($) {
  'use strict';

  app.DashboardView = Backbone.View.extend({
    el: '#app',
 
    initialize: function(props) {
      this.props = props;
      this.render();
    },

    template: _.template($('#dashboard-template').html()),

    render: function() {
      this.$el.html(this.template());

      var map = L.map('map')
        .setView([-8.7918741, 115.2269323], 16);

      L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
        maxZoom: 18,
        id: 'winnuayi.p1l11l5e',
        accessToken: 'pk.eyJ1Ijoid2lubnVheWkiLCJhIjoiY2lrM3A0cWl4MDAwOHY0a3RzOWx3MWQ2ZyJ9.oBxFuNtCJG68Cuu3DK5RWA'
      }).addTo(map);

      $('#alarm-table').DataTable();

      return this;
    },
  });
})(jQuery);
