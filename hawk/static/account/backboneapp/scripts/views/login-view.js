var app = app || {};

(function($) {
  'use strict';

  app.LoginState = new Backbone.Model({
    showLoginAlert: false,
    alertType: ''
  });

  app.LoginView = Backbone.View.extend({
    el: '#app',

    initialize: function() {
      this.listenTo(this.model, 'change:showLoginAlert',
                    this.renderMessageAlert);
      this.render();
    },

    template: _.template($('#login-template').html()),

    events: {
      'click #login-btn': 'postLogin',
      'click #forgot-password': 'postForgotPassword',
    },

    postLogin: function(e) {
      e.preventDefault();

      var model = this.model;

      var username = $('#username').val();
      var password = $('#password').val();

      if (!username || !password) {
        return;
      }

      $.ajax({
        url: '/accounts/api/login/',
        method: 'post',
        beforeSend: function(request) {
          request.setRequestHeader('X-CSRFToken', getCookie('csrftoken'))
        },
        data: { username: username, password: password },
        success: function(result) {
          localStorage.setItem('token', result.token);

          var tokenTimestamp = new Date().getTime(); 
          localStorage.setItem('tokenTimestamp', tokenTimestamp);

          // redirect to diesel (or general) dashboard
          window.location.replace(result.next);
        },
        error: function(result) {
          model.set('showLoginAlert', true);
        }
      });
    },

    postForgotPassword: function(e) {
      console.log('postForgotPassword');
    },

    render: function() {
      this.$el.html(this.template(this.model.toJSON()));
      return this;
    },

    renderMessageAlert: function() {
      this.messageAlertView = new app.MessageAlertView({
        message: 'Username or password does not match!'
      });
      this.messageAlertView.render();
    },
  });
})(jQuery);
