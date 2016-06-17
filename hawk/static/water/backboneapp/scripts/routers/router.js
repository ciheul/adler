var app = app || {};

(function($) {
  'use strict';

  var Router = Backbone.Router.extend({
    routes: {
      'detail': 'getDetail'
    },

    getDetail: function() {
      // $(document.body).append('Catalogue');
      console.log('hello');
      $('#app').empty();
      new app.DetailView().render();
    }
  });

  app.Router = new Router();
  Backbone.history.start();
})(jQuery);
