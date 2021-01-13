'use strict'

let friends = [];

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



// load friends data
function loadFriends(user_id) {
  let url = "/friends/" + user_id;
  let promise = ajax("GET", url);

  promise.then(
      (friendsList) => {
        friends = friendsList;
        console.log(friends);
        showFriends();
      }
  )
}

// show or refresh friend list
function showFriends() {
  let html = "<h3 class='text-left mb-4'>My Friends:</h3>"
  for (let i = 0; i < friends.length; i++) {
    html += `<p>${friends[i]}</p>`
  }
  document.getElementById("friends").innerHTML = html;
}

// send add friend request
function addFriend(user_id, friend_id, friend_name) {
  let url = `/addfriend/${user_id}/${friend_id}`;
  let promise = ajax("GET", url);

  promise.then(
      (b) => {
        if (b) {
          window.alert("add friend successfully");
          friends.unshift(friend_name);
          showFriends();
          let obj = document.getElementById(`item-${friend_id}`);
          obj.remove();
        } else {
          window.alert("add friend failed");
        }
      }
  )

}


