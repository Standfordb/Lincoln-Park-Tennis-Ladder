const socket = io({autoConnect: false});

document.getElementById("log-in").addEventListener("click", function() {
    socket.connect();
    socket.on("connect", function() {
        socket.emit("user_connect");
    })
})