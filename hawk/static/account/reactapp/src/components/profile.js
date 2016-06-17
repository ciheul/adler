"use strict";

import React from 'react';

import auth from '../auth';

export default class Profile extends React.Component {
  constructor(props) {
    super(props);
    this.state = { user: null };

    this.getProfile = this.getProfile.bind(this);
  }

  getProfile() {
    $.ajax({
      url: '/accounts/api/profile/',
      method: 'get',
      beforeSend: (request) => request.setRequestHeader('Authorization',
                                                        auth.getToken()),
      data: { },
      success: (result) => { this.setState({ user: result.user }); },
      error: (result) => { console.log(result); }
    });
  }

  componentWillMount() {
    this.getProfile();
  }

  render() {
    return (
      <div>
        <h1>Profile</h1>
        <ul>
          <li><a href="#" onClick={auth.logout}>Logout</a></li>
        </ul>
        <br />
        { this.state.user ? <ProfileDetail data={this.state.user} /> : null }
      </div>
    );
  }
}


class ProfileDetail extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <div>
        <h4>Detail</h4>
        <table className="table table-striped">
          <tbody>
          <tr>
            <td>Username</td><td>{this.props.data.username}</td>
          </tr>
          <tr>
            <td>First name</td><td>{this.props.data.firstName}</td>
          </tr>
          <tr>
            <td>Last name</td><td>{this.props.data.lastName}</td>
          </tr>
          <tr>
            <td>Email</td><td>{this.props.data.email}</td>
          </tr>
          </tbody>
        </table>
      </div>
    );
  }
}
