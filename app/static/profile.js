const socket = io();
const chatBox = document.getElementById("chat-box");
const allMatches = document.getElementById("all-matches");
const challengeMatches = document.getElementById("challenge-matches");
const checkbox = document.getElementById("filter");
const chatCol = document.getElementById("chat-col");
const recipient = document.getElementById("recipient").value;
const user = document.getElementById("user").value; 
const notificationCol = document.getElementById("notification-col");
const notificationBox = document.getElementById("notification-box");

notificationCol.style.display = "none";

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
    notificationCol.style.display = "";
}

notificationBox.addEventListener("click", event => {
    const isButton = event.target.nodeName === 'BUTTON';
    if (!isButton) {
        return;
    }

    if (event.target.name === "close") {
        let notification_id = event.target.id;
        socket.emit("remove_notification", notification_id);
    } else {
        let msg = event.target.id;
        let challenger_id = event.target.value;
        let notification_id = event.target.name;
        socket.emit("handle_challenge", msg, challenger_id, notification_id);
    }
})

socket.on("update_notifications", function(data) {
    let count = data.count;
    let id = data.id;
    let notification = document.getElementById(id);
    let profileBadge = document.getElementById("profile-badge");
    let buttonBadge = document.getElementById("button-badge");
    const content =`
        <div class="alert alert-secondary alert-dismissible fade show text-bg-secondary" style="font-size: .8em" role="alert">
            <strong>No notifications to show.</strong>
        </div>
        `

    if (count > 0) {
        profileBadge.innerHTML = count;
        buttonBadge.innerHTML = count;
        notification.style.display = "none";
    } else {
        profileBadge.style.display = "none";
        buttonBadge.style.display = "none";
        notification.style.display = "none";
        notificationBox.innerHTML += content;
    }


})