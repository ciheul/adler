'use strict';
import '../styles/styles.css';
var React = require('react');
var PureRenderMixin = require('react/lib/ReactComponentWithPureRenderMixin');
var _ = require('lodash');
var ReactGridLayout = require('react-grid-layout');

var BasicLayout = React.createClass({
  mixins: [PureRenderMixin],

  // propTypes: {
  //   onLayoutChange: React.PropTypes.func.isRequired,
  //   isDraggable: React.PropTypes.bool
  // },

  getDefaultProps() {
    return {
      className: "layout",
      items: 3,
      rowHeight: 30,
      cols: 12,
      isDraggable: true,
      isResizable: true
    };
  },

  getInitialState() {
    var layout = this.generateLayout();
    return {
      layout: layout
    };
  },

  generateDOM() {
    return _.map(_.range(this.props.items), function(i) {
      return (<div key={i}><span className="text">{i}</span></div>);
    });
  },

  generateLayout() {
    var p = this.props;
    return _.map(new Array(p.items), function(item, i) {
      var y = _.result(p, 'y') || Math.ceil(Math.random() * 4) + 1;
      return {x: i * 2 % 12, y: Math.floor(i / 6) * y, w: 2, h: y, i: i};
    });
  },

  onLayoutChange(layout) {
    // this.props.onLayoutChange(layout);
    this.setState({layout: layout});
  },

  render() {
    return (
      <ReactGridLayout layout={this.state.layout} onLayoutChange={this.onLayoutChange} {...this.props}>
        <div key={0}>
          <span className="text">0</span>
          <span className="react-resizable react-draggable"></span>
        </div>
        <div key={1}><span className="text">1</span></div>
        <div key={2}><span className="text">2</span></div>
      </ReactGridLayout>
    );
  }
});

module.exports = BasicLayout;

if (require.main === module) {
  require('./hook.js')(module.exports);
}
