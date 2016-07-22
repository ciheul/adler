"use strict";

import React from 'react';
import ReactDOM from 'react-dom';

import { IndexRoute, Link, Redirect, Route, Router } from 'react-router';

import Overview from './components/overview';
import NotFound from './components/notfound';
import Login from './components/login';
import BasicLayout from './components/gridsample';
import GridsterLayout from './components/gridstersample';

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
      <Route path="overview" component={Overview} />
      <Route path="basiclayout" component={BasicLayout} />
      <Route path="gridsterlayout" component={GridsterLayout} />
      <Route path="*" component={NotFound} />
    </Route>
  </Router>
);


ReactDOM.render(routes, document.getElementById('app'))
