'use strict';

// import Gridster from 'jquery.gridster';
import 'async';
import React from 'react';
import ReactDOM from 'react-dom';

export default class GridsterLayout extends React.Component {
  componentDidMount() {
    var gridster = $(this.findDOMNode()).gridster({
        widget_margins: [10, 10],
        widget_base_dimensions: [140, 140]
    }).data('gridster');
  }

  render() {
    return (
      <div>
        <h1>Gridster Layout</h1>
        <div className="gridster">
          <ul>
            <li data-row="1" data-col="1" data-sizex="1" data-sizey="1"></li>
            <li data-row="2" data-col="1" data-sizex="1" data-sizey="1"></li>
            <li data-row="3" data-col="1" data-sizex="1" data-sizey="1"></li>

            <li data-row="1" data-col="2" data-sizex="2" data-sizey="1"></li>
            <li data-row="2" data-col="2" data-sizex="2" data-sizey="2"></li>

            <li data-row="1" data-col="4" data-sizex="1" data-sizey="1"></li>
            <li data-row="2" data-col="4" data-sizex="2" data-sizey="1"></li>
            <li data-row="3" data-col="4" data-sizex="1" data-sizey="1"></li>

            <li data-row="1" data-col="5" data-sizex="1" data-sizey="1"></li>
            <li data-row="3" data-col="5" data-sizex="1" data-sizey="1"></li>

            <li data-row="1" data-col="6" data-sizex="1" data-sizey="1"></li>
            <li data-row="2" data-col="6" data-sizex="1" data-sizey="2"></li>
          </ul>
        </div>
      </div>
    );
  }
}
