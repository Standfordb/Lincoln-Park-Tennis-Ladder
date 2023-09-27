const socket = io();
const chatBox = document.getElementById("chat-box");

document.getElementById("chat-btn").addEventListener("click", function () {
    chatBox.scrollTop = chatBox.scrollHeight;
})

document.getElementById("send-form").addEventListener("submit", function () {
    let message = document.getElementById("message").value;
    socket.emit("chat_message", message);
    document.getElementById("message").value = "";
})

socket.on("chat_message", function(data) {
    createMessage(data.sender, data.message, data.time);
})

const createMessage = (sender, msg, time) => {
    const content = `
    <p>
        <strong>${sender}</strong>: ${msg}  <span class="muted">${time}</span>
    </p
    `
    chatBox.innerHTML += content;
    chatBox.scrollTop = chatBox.scrollHeight;
}
