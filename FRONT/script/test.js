'use strict';
const getLdr = function() {
  handleData(`http://${ip}:5000/api/ldr`, showLdr);
};
const showgpsdata = function(data) {
  console.log(data);
};

const showLdr = function(data) {
  document.querySelector('.js-ldr').innerHTML = data;
};
const init = function() {
  getLdr();
};
const refresh = function() {
  getLdr();
};

const sonicOn = function() {
  document.querySelector('.js-sonic').innerHTML = 'on';
};
const sonicOff = function() {
  document.querySelector('.js-sonic').innerHTML = 'off';
};

const reedOff = function() {
  document.querySelector('.js-reed').innerHTML = 'off';
};
const reedOn = function() {
  document.querySelector('.js-reed').innerHTML = 'on';
};

const showGps = function(data) {
  console.log(data);
  document.querySelector('.js-gps').innerHTML = `lat: ${data.lat} <br> long: ${
    data.long
  }`;
};

document.addEventListener('DOMContentLoaded', function() {
  console.info('DOM geladen');
  init();
  initmaps();
  document.querySelector('.js-button').addEventListener('click', refresh);
  socket.addEventListener('sonic_on', sonicOn);
  socket.addEventListener('sonic_off', sonicOff);
  socket.addEventListener('reedOn', reedOn);
  socket.addEventListener('reedOff', reedOff);
  socket.addEventListener('gps', showGps);
});
