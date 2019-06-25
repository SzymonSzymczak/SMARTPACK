'use strict';
let mymap;

const showMapRoute = function(data) {
  document.querySelector('.js-map').innerHTML =
    '<a href="saved_routes.html"><div class="c-map__back">Back</div></a>';
  document.querySelector('.js-map').classList += 'c-map';
  let arrCoord = [];
  mymap = L.map('js-map').setView([data[0].Latitude, data[0].Longitude], 12);
  L.tileLayer.provider('OpenStreetMap').addTo(mymap);
  for (let coord of data) {
    let lat = coord.Latitude;
    let lon = coord.Longitude;
    arrCoord.push([lat, lon]);
  }
  L.polyline(arrCoord, {
    color: 'red',
    weight: 10
  }).addTo(mymap);
  let point = L.marker([arrCoord[0][0], arrCoord[0][1]], {
    title: `Start`,
    color: 'red'
  }).addTo(mymap);
  let pointEnd = L.marker(
    [arrCoord[arrCoord.length - 1][0], arrCoord[arrCoord.length - 1][1]],
    {
      title: `End`,
      color: 'red'
    }
  ).addTo(mymap);
};

const getCoordinates = function(id) {
  handleData(`http://${ip}:5000/api/savedroutes/${id}`, showMapRoute);
};

const showRoutes = function(data) {
  let object = document.querySelector('.js-routes');
  object.innerHTML = '';
  for (let route of data) {
    object.innerHTML += `<div class="c-route" routeid="${route.id}">
        <p>${route.name}</p>
        <p>${route.date.slice(0, -13)}</p>
      </div>
      `;
    for (let child of object.children) {
      child.addEventListener('click', function() {
        getCoordinates(child.getAttribute('routeid'));
      });
    }
  }
};

document.addEventListener('DOMContentLoaded', function() {
  console.info('DOM geladen');
  handleData(`http://${ip}:5000/api/savedroutes`, showRoutes);
});
