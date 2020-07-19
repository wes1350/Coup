var socket = io();

$(document).ready(function(){ 
    $("button#room-button").click(function(event) {
        console.log('Joining room:' + event.target.innerHTML)
        socket.emit('join room', event.target.innerHTML);
    })
}); 
