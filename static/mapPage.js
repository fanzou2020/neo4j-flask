'use strict'

let map, selectedState, selectedCity, selectedCategory, businessData;
let markers = [];
let dict = new Map();
let markerCluster;

function initMap() {
  // const map_center = { lat: businessData[0]["latitude"], lng: businessData[0]["longitude"] }
  const map_center = {lat: 45.502654, lng: -73.555256};

  map = new google.maps.Map(document.getElementById("map"), {
    center: map_center,
    zoom: 8,
  });

  markerCluster = new MarkerClusterer(map, markers, {
    imagePath: "static/images/m"
  })
}

function loadMarkers() {
  // set center to city
  const new_center = new google.maps.LatLng(businessData[0]["latitude"], businessData[0]["longitude"]);
  map.panTo(new_center);

  // create markers
  console.log(businessData);
  clearMarkers();
  map.setZoom(12);
  for (let i = 0; i < businessData.length; i++) {
    let b = businessData[i];
    let marker = new google.maps.Marker({
      position: new google.maps.LatLng(b["latitude"], b["longitude"]),
    });

    // associate business node and markers in a dictionary
    dict.set(b, marker);

    // add infoWindow on marker
    marker.addListener("click", () => {
      const contentString = `
      <div id="infoWindow">
      <div id="siteNotice"></div>
      <h5>${b["name"]}</h5>
      <p><b>Stars: ${b["stars"]}</b></p>
      <p><b>Review count: ${b["review_count"]}</b></p>
      <p>Address: ${b["address"]}</p>
      <p>City: ${b["city"]}</p>
      <p>State: ${b["state"]}</p>
      <p>Postal code: ${b["postal_code"]}</p>
      </div>
      `;

      const infoWindow = new google.maps.InfoWindow({
        content: contentString
      });
      infoWindow.open(map, marker);
    })

    markers.push(marker);
  }

  // create marker cluster
  markerCluster = new MarkerClusterer(map, markers, {
    imagePath: "static/images/m"
  })

  // setMapOnAll(map);
}

function clearMarkers() {
  setMapOnAll(null);
  markers = [];
  dict = new Map();
  markerCluster.clearMarkers();
}

function setMapOnAll(map) {
  for (let i = 0; i < markers.length; i++) {
    markers[i].setMap(map);
  }
}


function loadSideBarContent() {
  let html = "";
  for (let i = 0; i < businessData.length; i++) {
    let b = businessData[i];
    html += `<p><span id="item-${i}">${b["name"]}</span></p>`;
  }
  document.getElementById("sideBarContent").innerHTML = html;

  // add click event handler to sidebar element
  for (let i = 0; i < businessData.length; i++) {
    let b = businessData[i];
    document.getElementById(`item-${i}`).onclick = () => {
      const contentString = `
      <div id="infoWindow">
      <div id="siteNotice"></div>
      <h5>${b["name"]}</h5>
      <p><b>Stars: ${b["stars"]}</b></p>
      <p><b>Review count: ${b["review_count"]}</b></p>
      <p>Address: ${b["address"]}</p>
      <p>City: ${b["city"]}</p>
      <p>State: ${b["state"]}</p>
      <p>Postal code: ${b["postal_code"]}</p>
      </div>
      `;

      const infoWindow = new google.maps.InfoWindow({
        content: contentString
      });

      let marker = dict.get(b);

      map.panTo(marker.position);
      map.setZoom(20);
      infoWindow.open(map, marker);
    };
  }
}

function sortByReviewCount() {
  businessData.sort((a, b) => { return b["review_count"] - a["review_count"] });
  loadSideBarContent();
}

function sortByStars() {
  businessData.sort((a, b) => { return b["stars"] - a["stars"] });
  loadSideBarContent();
}


// return a promise
function ajax(method, url, data) {
  return new Promise((resolve, reject) => {
    let request = new XMLHttpRequest();
    request.open(method, url);
    request.onload = function () {
      if (request.status === 200) {
        let jsonResponse = JSON.parse(request.responseText)
        resolve(jsonResponse);
      } else {
        reject(request.status);
      }
    }
    request.send();
  })
}

// when select a state, show cities in this state
function stateOnChange(t) {
  let select = document.getElementById("state-select");
  let index = select.selectedIndex;
  let state = select.options[index].value;
  console.log(state);
  selectedState = state;

  let promise = ajax("GET", "/cities/" + state);
  promise.then(
      (cities) => {
        console.log(cities);
        let optionList = "<option value='' selected>Select a city</option>";
        for (let i = 0; i < cities.length; i++) {
          optionList += `<option value='${cities[i]}'>${cities[i]}</option>`
        }
        document.getElementById("city-select").innerHTML = optionList;
      }
  )
  .catch((status) => {
    console.log(status);
  });
}

// when select a city, show categories in this city
function cityOnChange(t) {
  let select = document.getElementById("city-select");
  let index = select.selectedIndex;
  let city = select.options[index].value;
  console.log(city);
  selectedCity = city;

  let promise = ajax("GET", "/categories/" + city);
  promise.then(
      (categories) => {
        console.log(categories);
        let optionList = "<option value='' selected>Select a category</option>";
        for (let i = 0; i < categories.length; i++) {
          optionList += `<option value='${categories[i]}'>${categories[i]}</option>`
        }
        document.getElementById("category-select").innerHTML = optionList;
      }
  )
  .catch((status) => {
    console.log(status);
  });
}

// when select a category, set global variable selectedCategory
function categoryOnChange(t) {
  let select = document.getElementById("category-select");
  let index = select.selectedIndex;
  let category = select.options[index].value;
  selectedCategory = encodeURIComponent(category);
  console.log(selectedCategory);
}

// when click submit button, submit selected options to backend, return data of businesses
function onClickSubmit() {
  let url = encodeURI(`/business?state=${selectedState}&city=${selectedCity}&category=${selectedCategory}`);
  let promise = ajax("GET", url);
  promise.then(
      (value) => {
        businessData = value;
        loadMarkers();

        loadSideBarContent();
      }
  )
  .catch(
      (error) => {
        console.log(error);
      }
  )
}
