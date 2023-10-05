const checkbox = document.getElementById("friendly");
const challengeOpponents = document.getElementById("challenge-opponents");
const friendlyOpponents = document.getElementById("friendly-opponents");
const opponent = document.getElementsByName("opponent");
const challOpps = document.getElementById("chall-opps");
const friendlyOpps = document.getElementById("friendly-opps");

checkbox.addEventListener("change", function() {
    if (checkbox.checked) {
        challengeOpponents.style.display = "none";
        friendlyOpponents.style.display = "";
        challOpps.selectedIndex = 0;
        friendlyOpps.selectedIndex = 0;
    } else {
        friendlyOpponents.style.display = "none";
        challengeOpponents.style.display = "";
        challOpps.selectedIndex = 0;
        friendlyOpps.selectedIndex = 0;
    }
})

