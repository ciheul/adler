"use strict";

import 'bootstrap/dist/css/bootstrap.css';
import '../styles/login.css';
import 'jquery';

import React from 'react';
import Modal from 'react-modal';

import auth from '../auth';
import { getCookie, validateEmailRegex } from '../utility';
import classNames from 'classnames';


const customStyles = {
  overlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.75)'
  },
  content : {
    position                   : 'relative',
    top                        : 40,
    left                       : 40,
    right                      : 40,
    bottom                     : 40,
    border                     : '0px solid #ccc',
    // background                 : 'red',
    // overflow                   : 'auto',
    WebkitOverflowScrolling    : 'touch',
    borderRadius               : '6px',
    outline                    : 'none',
    padding                    : '0'
  }
};

export default class Login extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      username: '',
      password: '', 
      showLoginAlert: false,

      showModal: false,
      showForgotPasswordAlert: false,
      forgotPasswordMessage: '',
      email: ''
    };

    this.handleUsername = this.handleUsername.bind(this);
    this.handlePassword = this.handlePassword.bind(this);
    this.postLogin = this.postLogin.bind(this);

    this.handleEmail = this.handleEmail.bind(this);
    this.postForgotPassword = this.postForgotPassword.bind(this);
    this.openModal = this.openModal.bind(this);
    this.closeModal = this.closeModal.bind(this);
  }

  ////////// LOGIN FORM //////////

  handleUsername(e) {
    this.setState({ username: e.target.value });
  }

  handlePassword(e) {
    this.setState({ password: e.target.value });
  }

  postLogin(e) {
    e.preventDefault();

    var username = this.state.username.trim();
    var password = this.state.password.trim();

    if (!username || !password) {
      return;
    }
    // TODO use vanillaJS
    $.ajax({
      url: '/accounts/api/login/',
      method: 'post',
      beforeSend: (request) => request.setRequestHeader('X-CSRFToken',
                                                        getCookie('csrftoken')),
      data: { username: username, password: password },
      success: (result) => {
        localStorage.setItem('token', result.token);

        let tokenTimestamp = new Date().getTime(); 
        localStorage.setItem('tokenTimestamp', tokenTimestamp);

        // redirect to diesel (or general) dashboard
        window.location.replace(result.next);
      },
      error: (result) => {
        this.setState({ showLoginAlert: true });
      }
    });
  }

  ////////// FORGOT PASSWORD FORM //////////

  handleEmail(e) {
    this.setState({ email: e.target.value });
  }

  openModal() {
    // reset everything from previous action
    this.setState({ showModal: true, email: '' });
    this.setMessageAlert(false, '');
  }

  closeModal() {
    this.setState({ showModal: false });
  }

  validateEmailForm(email) {
    let result = true;

    // if empty, autofocus to form and solid border with red color
    if (!email) {
      this.setMessageAlert(true, 'Please input your email.');
      return false;
    }

    if (validateEmailRegex(email) === false) {
      this.setMessageAlert(true, 'Invalid email format.');
      return false;
    }

    return true;
  }

  setMessageAlert(isShown, message, type='alert-danger') {
    this.setState({ 
      showForgotPasswordAlert: isShown,
      forgotPasswordMessage: message,
      alertType: type
    });
  }

  postForgotPassword(e) {
    e.preventDefault();

    if (this.validateEmailForm(this.state.email) === false)
      return;

    // send    
    $.ajax({
      url: '/accounts/api/forgotpassword/',
      method: 'post',
      beforeSend: (request) => {
        request.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
      },
      data: { email: this.state.email },
      success: (result) => {
        this.setMessageAlert(true,
                             'An instruction has been sent to your email.',
                             'alert-success')
      },
      error: (result) => {
        let responseText = JSON.parse(result.responseText);
        this.setMessageAlert(true, responseText.message);
      }
    });
  }

  render() {
    return (
      <div>
        <h1>INetSCADA</h1>
        <div className="login-form">
          <form onSubmit={this.postLogin} method="post" className="form-horizontal" role="form">
            { this.state.showLoginAlert ? <MessageAlert message="Username or password does not match!" alertType="alert-warning"/> : null }
            <div className="form-group">
              <input id="username" name="username" className="form-control" type="text" placeholder="username" value={this.state.username} onChange={this.handleUsername} required autofocus />
            </div>

            <div className="form-group">
              <input type="password" name="password" className="form-control" placeholder="password" value={this.state.password} onChange={this.handlePassword} required />
            </div>

            <div className="form-group">
              <button id="login-btn" className="btn btn-md btn-primary btn-group-justified" type="submit">Login</button>
            </div>
        
            <div className="form-group">
              <a href="#" onClick={this.openModal} className="forgot-password">Forgot your password?</a>
            </div>
          </form>

          <Modal className="Modal__Bootstrap modal-dialog"
                 isOpen={this.state.showModal}
                 onRequestClose={this.closeModal}
                 style={customStyles}>

            <div className="modal-content">
              <div className="modal-header">
                <button type="button" className="close" onClick={this.closeModal}>
                  <span aria-hidden="true">&times;</span>
                  <span className="sr-only">Close</span>
                </button>
                <h4>Forgot Password?</h4>
              </div>

              <div className="modal-body">
                <div>Please input your email. We will send a link to change your password.</div>
                <br />
                { this.state.showForgotPasswordAlert ? <MessageAlert message={this.state.forgotPasswordMessage} alertType={this.state.alertType} /> : null }
                <form onSubmit={this.postForgotPassword} method="post" role="form">
                  <input type="text" name="email" className="form-control" placeholder="email" value={this.state.email} onChange={this.handleEmail} autofocus />
                </form>
              </div>

              <div className="modal-footer">
                <button id="cancel-btn" className="btn btn-md btn-default" type="button" onClick={this.closeModal}>Cancel</button>
                <button id="send-btn" className="btn btn-md btn-primary" type="submit" onClick={this.postForgotPassword}>Send</button>
              </div>
            </div>
          </Modal>
        </div>

      </div>
    );
  }
}


class MessageAlert extends React.Component {
  render() {
    var alertClass = classNames(this.props.alertType, {
      'form-group': true,
      'alert': true,
    });

    return (<div className={alertClass}>{this.props.message}</div>);
  }
}
