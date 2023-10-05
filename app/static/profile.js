const socket = io();
const chatBox = document.getElementById("chat-box");
const allMatches = document.getElementById("all-matches");
const challengeMatches = document.getElementById("challenge-matches");
const checkbox = document.getElementById("filter");
const chatCol = document.getElementById("chat-col");
const recipient = document.getElementById("recipient").value;
const user = document.getElementById("user").value; 

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
    if (data.sender == recipient || data.sender == user) {
        createMessage(data.name, data.message, data.time);
    }
})

checkbox.addEventListener("change", function() {
    if (checkbox.checked) {
        allMatches.style.display = "none";
        challengeMatches.style.display = "";
    } else {
        allMatches.style.display = "";
        challengeMatches.style.display = "none"
    }
})

if (user == recipient || Boolean(user) == false) {
    chatCol.style.display = "none";
}