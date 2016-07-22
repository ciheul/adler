"use strict";

import 'jquery';

import { getCookie } from './utility';


class Auth {
  isAuthenticated() {
    return !!localStorage.token;
  }

  getToken() {
    return localStorage.token;
  }

  logout(e) {
    e.preventDefault();

    $.ajax({
      url: '/accounts/api/logout/',
      method: 'post',
      beforeSend: (request) => request.setRequestHeader('X-CSRFToken',
                                                        getCookie('csrftoken')),
      data: { },
      success: (result) => {
        localStorage.removeItem('token');
        localStorage.removeItem('tokenTimestamp');

        // redirect to login page
        window.location.replace(result.next);
      },
      error: (result) => {
        console.log(result);
      }
    });

  }
}


let auth = new Auth();
module.exports = auth;
