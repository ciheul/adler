var app = app || {};

(function($) {
  'use strict';

  app.DetailView = Backbone.View.extend({
    el: '#app',

    initialize: function(props) {
      this.props = props;
      this.render();
    },

    template: _.template($('#detail-template').html()),

    render: function() {
      this.$el.html(this.template());
    },
  });
})(jQuery);
