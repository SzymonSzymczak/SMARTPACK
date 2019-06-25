'use strict';

const showSettings = function(json) {
  console.log(json.Auto_light);
  if (json.Auto_light == 'on') {
    document.querySelector('#Auto_light').checked = 1;
  } else {
    document.querySelector('#Auto_light').checked = 0;
  }
  if (json.GPS == 'on') {
    document.querySelector('#GPS').checked = 1;
  } else {
    document.querySelector('#GPS').checked = 0;
  }
  if (json.Inside_light == 'on') {
    document.querySelector('#Inside_light').checked = 1;
  } else {
    document.querySelector('#Inside_light').checked = 0;
  }
  document.querySelector('#Light_mode').value = json.Light_mode;
};

const sendSettingToggle = function(id) {
  let object = document.querySelector(`#${id}`);
  if (object.checked) {
    socket.emit('changeSetting', [id, 'on']);
  } else {
    socket.emit('changeSetting', [id, 'off']);
  }
};
const sendSettingSelect = function(id) {
  let object = document.querySelector(`#${id}`);
  socket.emit('changeSetting', [id, object.value]);
};

const listenToSettings = function() {
  document.querySelector('#Auto_light').addEventListener('input', function() {
    sendSettingToggle('Auto_light');
  });
  document.querySelector('#GPS').addEventListener('input', function() {
    sendSettingToggle('GPS');
  });
  document.querySelector('#Inside_light').addEventListener('input', function() {
    sendSettingToggle('Inside_light');
  });
  document.querySelector('#Light_mode').addEventListener('input', function() {
    sendSettingSelect('Light_mode');
  });
};

const init = function() {
  handleData(`http://${ip}:5000/api/settings`, showSettings);
  listenToSettings();
};

document.addEventListener('DOMContentLoaded', function() {
  console.info('DOM geladen');
  init();
  initmaps();
});
