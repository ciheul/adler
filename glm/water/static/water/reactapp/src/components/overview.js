"use strict";

// import 'bootstrap/dist/css/bootstrap.css';
// import '../styles/base.css';
// import 'react-grid-layout/css/styles.css';
import 'jquery';

import React from 'react';
import ReactDOM from 'react-dom';
import ReactGridLayout from 'react-grid-layout';
import _ from 'lodash';

import { getCookie } from '../utility.js';


export default class Overview extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      layout: this.generateLayout()
    };
  }

  generateDOM() {
    return _.map(_.range(this.props.items), function(i) {
      return (<div key={i}><span className="text">{i}</span></div>);
    });
  }

  generateLayout() {
    var p = this.props;
    return _.map(new Array(p.items), function(item, i) {
      var y = _.result(p, 'y') || Math.ceil(Math.random() * 4) + 1;
      return {x: i * 2 % 12, y: Math.floor(i / 6) * y, w: 2, h: y, i: i};
    });
  }

  render() {
    return (
      <div>
        <h1>ElectricalOverview</h1>
        <ul>
          <li><a href="/accounts/#/profile/">My Profile</a></li>
          <li><a href="/accounts/logout/">Logout</a></li>
        </ul>
        <ReactGridLayout className="layout" layout={this.state.layout}
            onLayoutChange={this.onLayoutChange} items={20} rowHeight={30} cols={12}>
          <div key={1}>1</div>
          <div key={2}>2</div>
          <div key={3}>3</div>
        </ReactGridLayout>
      </div>
    ); 
  }
}


// ReactDOM.render(<ElectricalOverview />, app);
