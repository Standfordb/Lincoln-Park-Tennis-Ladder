const socket = io();
const chatBox = document.getElementById("chat-box");

document.getElementById("chat-btn").addEventListener("click", function () {
    chatBox.scrollTop = chatBox.scrollHeight;
})

// Create a new message display
const createMessage = (sender, msg, time) => {
    const content = `
    <p>
        <strong>${sender}</strong>: ${msg}  <span class="muted">${time}</span>
    </p
    `
    chatBox.innerHTML += content;
    chatBox.scrollTop = chatBox.scrollHeight;
}

//Handle private messages on profile.html
document.getElementById("private-msg-form").addEventListener("submit", function () {
    let message = document.getElementById("message").value;
    let recipient = document.getElementById("recipient").value;
    socket.emit("private_message", message, recipient);
    document.getElementById("message").value = "";
})

socket.on("private_message", function(data) {
    let recipient = document.getElementById("recipient").value;
    let user = document.getElementById("user").value;
    if (data.sender == recipient || data.sender == user) {
        createMessage(data.name, data.message, data.time);
    }
})