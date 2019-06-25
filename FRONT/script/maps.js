'use strict';
let mymap;
// let coordiates = [];
// let coordiantes = [
//   [50.8821, 3.28599],
//   [50.8821, 3.28599],
//   [50.8821, 3.286],
//   [50.8821, 3.28],
//   [50.8821, 3.286]
// ];
const colors = [
  'blue',
  'red',
  'purple',
  'black',
  'pink',
  'orange',
  'brown',
  'yellow'
];

const routesaved = function(data) {
  if (data.savestatus == 0) {
    document.querySelector('.c-map__save').innerHTML = 'Route already saved!';
  } else {
    document.querySelector('.c-map__save').innerHTML = 'Saved!';
  }
};

const sendRoute = function() {
  let id = document.querySelector('.c-map__save').getAttribute('routeid');
  name = document.querySelector('#routename').value;
  console.log(id);
  console.log(name);
  if (name) {
    socket.emit('saveroute', [id, name]);
    socket.addEventListener('routesaved', routesaved);
  } else {
    document.querySelector('.c-map__save').innerHTML = 'Name canot be empty!';
  }
};

const save_route = function(routeid, e) {
  mymap.setView(e.latlng, 13);
  document.querySelector(
    '.c-map__save'
  ).innerHTML = `Choose a name <br> <input id="routename" type="text"></input><button id="buttonSaveRoute">Ok</button>`;
  document.querySelector('.c-map__save').setAttribute('routeid', routeid);
  document
    .querySelector('#buttonSaveRoute')
    .addEventListener('click', sendRoute);
};

const showroute = function(json) {
  let arrayRoutes = [];
  let coordinates = [];
  if (json == []) {
    // console.log(json);
    mymap = L.map('js-map').setView([50.8821, 3.286], 10);
    L.tileLayer.provider('OpenStreetMap').addTo(mymap);
  } else {
    mymap = L.map('js-map').setView([json[0].Latitude, json[0].Longitude], 10);
    L.tileLayer.provider('OpenStreetMap').addTo(mymap);
    console.log(parseInt(json[0].countRouteId));
    for (let i = 0; i <= parseInt(json[0].countRouteId); i++) {
      let coordinates = [];
      for (let coordinate of json) {
        if (coordinate.todaysRouteId == i) {
          let single = [coordinate.Latitude, coordinate.Longitude];
          coordinates.push(single);
        }
      }
      console.log(coordinates);
      if (coordinates.length > 0) {
        let polyline = L.polyline(coordinates, {
          color: colors[i],
          weight: 10,
          title: `Route: ${i}`
        })
          .addTo(mymap)
          .on('click', function(e) {
            save_route(i, e);
          });
        let point = L.marker([coordinates[0][0], coordinates[0][1]], {
          title: `Route: ${i}`,
          color: colors[i]
        })
          .addTo(mymap)
          .on('click', function(e) {
            save_route(i, e);
          });
        let pointEnd = L.marker(
          [
            coordinates[coordinates.length - 1][0],
            coordinates[coordinates.length - 1][1]
          ],
          {
            title: `Route: ${i}`,
            color: colors[i]
          }
        )
          .addTo(mymap)
          .on('click', function(e) {
            save_route(i, e);
          });
      }
      arrayRoutes[i] = coordinates;
    }
  }
};

const initmaps = function() {
  handleData(`http://${ip}:5000/api/gpsdata`, showroute);
};
