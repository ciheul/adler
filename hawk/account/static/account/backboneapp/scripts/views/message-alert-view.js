var app = app || {};

(function($) {
  'use strict';

  app.MessageAlertView = Backbone.View.extend({
    el: '#message-alert',
  
    initialize: function(props) {
      this.props = props;
    },

    template: _.template($('#message-alert-template').html()),

    render: function() {
      this.$el.html(this.template({ message: this.props.message }));
      return this;
    },
  });
})(jQuery);
