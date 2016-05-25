"use strict";

import React from 'react';
import ReactDOM from 'react-dom';

import { IndexRoute, Link, Redirect, Route, Router } from 'react-router';

import Login from './components/login';
import NotFound from './components/notfound';
import Profile from './components/profile';

import auth from './auth';


let requireAuthentication = (nextState, replaceState) => {
  if (!auth.isAuthenticated()) {
    replaceState({ nextPathname: nextState.location.pathname }, '/login');
  }
}


class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      isAuthenticated: auth.isAuthenticated()
    };
  }

  render() {
    return (
      <div className="container">
        <div>{this.props.children}</div>    
      </div>
    );
  }
}


let routes = (
  <Router>
    <Route path="/" component={App}>
      // <IndexRoute component={Login} />
      <Route path="login" component={Login} />
      <Route path="profile" component={Profile} onEnter={requireAuthentication} />
      <Route path="*" component={NotFound} />
    </Route>
  </Router>
);

ReactDOM.render(routes, document.getElementById('app'))
