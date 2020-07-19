var socket = io();
// var socket = io('http://localhost:5000');

// Upon redirection to the room.html page, join the room specified in the URL

function joinRoom(room){
  socket.emit('join_room', room)
}

socket.on('message', function(msg) {
    console.log(msg)
    document.getElementById("info").innerText = msg
});
socket.on('settings', function(msg) {
    console.log(msg)
    document.getElementById("settings").innerText = msg
});
socket.on('state', function(msg) {
    console.log(msg)
    document.getElementById("state").innerText = msg
});
socket.on('state_json', function(msg) {
    console.log(msg)
});
socket.on('prompt', function(msg) {
    console.log(msg)
    document.getElementById("prompt").innerText = msg
});
socket.on('error', function(msg) {
    console.log(msg)
    document.getElementById("error").innerText = msg
});
socket.on('info', function(msg) {
    console.log(msg)
    document.getElementById("info").innerText = msg
});
socket.on('start game', function(msg) {
    document.getElementById("info").innerText = msg
    $("div.action-container").show();
    $("#start-button").hide();
    $("button.bot-button").hide();
});
$(document).ready(function(){ 
    $("button#start-button").click(function() {
        console.log('starting game')
        socket.emit('start game');
    })
    $("button.bot-button").click(function() {
        console.log('adding bot')
        socket.emit('add_bot');
    })
    $("button#submission").click(function(){ 
        console.log("Got a click!!!");
        socket.emit('action', $("#actions").val());
        document.getElementById("actions").value = "";
    }) 
    $("button.action-button").click(function(event){
        console.log("Got a action-button click");
        socket.emit('action', event.target.innerHTML)
    })
    $("button#pass-button").click(function(event){
        console.log("Passing");
        socket.emit('action', "n");
    })
}); 
