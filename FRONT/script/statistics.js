'use strict';
let objectFrom;
let objectTo;
let myChart = 0;

const refreshGraph = function() {
  let valFrom = objectFrom.value;
  let valTo = objectTo.value;
  let body = `{
    "dateFrom" : "${valFrom}",
    "dateTo" : "${valTo}"
  }`;
  //   body = JSON.parse(body);
  handleData(`http://${ip}:5000/api/statistics`, showStats, 'POST', body);
};

const showStats = function(json) {
  let arrSpeed = [];
  let arrTime = [];
  let totalSpeed = 0;
  for (let element of json) {
    arrSpeed.push(element.Speed);
    totalSpeed += element.Speed;
    arrTime.push(element.DateTime);
  }
  let avgSpeed = totalSpeed / arrSpeed.length;
  let ctx = document.getElementById('js-chart').getContext('2d');
  //   ctx.height = 1000;
  console.log(arrSpeed);
  console.log(avgSpeed);
  if (myChart == 0) {
    myChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: arrTime,
        datasets: [
          {
            label: 'Speed',
            data: arrSpeed,
            backgroundColor: 'rgba(0,0,0,0)',
            borderColor: 'red'
          }
        ]
      }
    });

    objectFrom.addEventListener('input', refreshGraph);
    objectTo.addEventListener('input', refreshGraph);
  } else {
    myChart.data.labels = arrTime;
    myChart.data.datasets[0].data = arrSpeed;
    myChart.update();
  }
  document.querySelector(
    '.c-statistics__stats'
  ).innerHTML = `<h3>Average Speed</h3>
  <p>${avgSpeed}</p>`;
};

const showDates = function(json) {
  objectFrom.innerHTML = '';
  objectTo.innerHTML = '';
  for (let date of json.reverse()) {
    let dateFormatted =
      String(date.dates).slice(8, 10) +
      '/' +
      String(date.dates).slice(5, 7) +
      '/' +
      String(date.dates).slice(0, 4);
    objectFrom.innerHTML += `<option value="${
      date.dates
    }">${dateFormatted}</option>`;
    objectTo.innerHTML += `<option value="${
      date.dates
    }">${dateFormatted}</option>`;
  }
  let LastDate = json[0].dates;
  let body = `{
    "dateFrom" : "${LastDate}",
    "dateTo" : "${LastDate}"
  }`;
  //   body = JSON.parse(body);
  handleData(`http://${ip}:5000/api/statistics`, showStats, 'POST', body);
};

document.addEventListener('DOMContentLoaded', function() {
  console.info('DOM geladen');
  objectFrom = document.querySelector('#date-from');
  objectTo = document.querySelector('#date-to');
  handleData(`http://${ip}:5000/api/init_statistics`, showDates);
});
