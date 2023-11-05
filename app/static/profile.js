const socket = io();
const chatBox = document.getElementById("chat-box");
const allMatches = document.getElementById("all-matches");
const challengeMatches = document.getElementById("challenge-matches");
const checkBox = document.getElementById("filter");
const chatCol = document.getElementById("chat-col");
const user = document.getElementById("user").value;
const profile = document.getElementById("profile").value;
const notificationCol = document.getElementById("notification-col");
const notificationBox = document.getElementById("notification-box");
const h2hT = document.getElementById("h2h-t");
const h2hC = document.getElementById("h2h-c");


if (user == '0') {
    notificationCol.style.display = "none";
    chatCol.style.display = "none";
    h2hT.style.display = "none"
    h2hC.style.display = "none"
} else if (user == profile) {
    chatCol.style.display = "none";
    h2hT.style.display = "none"
    h2hC.style.display = "none"
} else {
    notificationCol.style.display = "none";
}



document.getElementById("chat-btn").addEventListener("click", function (event) {
    if (event.target.classList.contains("collapsed")) {
        socket.emit("leave_room", user, profile);
    } else {
        socket.emit("join_room", user, profile)
        chatBox.scrollTop = chatBox.scrollHeight;
        }
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
    socket.emit("private_message", message, profile);
    document.getElementById("message").value = "";
})

socket.on("private_message", function(data) {
    if (data.sender == profile || data.sender == user) {
        createMessage(data.name, data.message, data.time);
    }
})

checkBox.addEventListener("change", function() {
    if (checkBox.checked) {
        allMatches.style.display = "none";
        challengeMatches.style.display = "";
    } else {
        allMatches.style.display = "";
        challengeMatches.style.display = "none";
    }
})

notificationBox.addEventListener("click", event => {
    const isButton = event.target.nodeName === 'BUTTON';
    if (!isButton) {
        return;
    }

    if (event.target.name === "close") {
        let id = event.target.id;
        socket.emit("remove_notification", id);
    } else if (event.target.name === "profile-btn") {
        let id = event.target.id
        socket.emit("remove_notification", id)
    } else {
        let msg = event.target.name;
        let challenger_id = event.target.value;
        let notification_id = event.target.id;
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
        if (notification) {
            notification.style.display = "none";
        }
        notificationBox.innerHTML += content;
    }


})

socket.on("error_open_challenge", function(data) {
    let notification = document.getElementById(data.id)
    let content =`
        <span id="error-${data.id}">${data.msg}</span>
    `
    if (document.getElementById("error-" + data.id)) {
        return
    } else {
        notification.innerHTML += content;
    }
})