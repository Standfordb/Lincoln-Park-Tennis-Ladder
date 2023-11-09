const checkbox = document.getElementById("friendly");
const matchType = document.getElementById("type");
const challengeOpponents = document.getElementById("challenge-opponents");
const friendlyOpponents = document.getElementById("friendly-opponents");
const challOpps = document.getElementById("chall-opps");
const friendlyOpps = document.getElementById("friendly-opps");
const firstTiebreak = document.getElementById("1st-tiebreak");
const secondTiebreak = document.getElementById("2nd-tiebreak");
const thirdTiebreak = document.getElementById("3rd-tiebreak");
const firstTieCheck = document.getElementById("1st-tie-check");
const secondTieCheck = document.getElementById("2nd-tie-check");
const thirdTieCheck = document.getElementById("3rd-tie-check");
const firstTieWinner = document.getElementById("1st-tie-winner");
const firstTieLoser = document.getElementById("1st-tie-loser");
const secondTieWinner = document.getElementById("2nd-tie-winner");
const secondTieLoser = document.getElementById("2nd-tie-loser");
const thirdTieWinner = document.getElementById("3rd-tie-winner");
const thirdTieLoser = document.getElementById("3rd-tie-loser");


checkbox.addEventListener("change", function() {
    if (checkbox.checked) {
        challengeOpponents.style.display = "none";
        friendlyOpponents.style.display = "";
        friendlyOpps.selectedIndex = 0;
        matchType.value = "Friendly";
    } else {
        friendlyOpponents.style.display = "none";
        challengeOpponents.style.display = "";
        friendlyOpps.selectedIndex = 0;
        matchType.value = "CHALLENGE";
    }
})

firstTieCheck.addEventListener("change", function() {
    if (firstTieCheck.checked) {
        firstTiebreak.style.display = "";
    } else {
        firstTiebreak.style.display = "none";
        firstTieWinner.value = "None";
        firstTieLoser.value = "None"
    }
})

secondTieCheck.addEventListener("change", function() {
    if (secondTieCheck.checked) {
        secondTiebreak.style.display = "";
    } else {
        secondTiebreak.style.display = "none";
        secondTieWinner.value = "None";
        secondTieLoser.value = "None";
    }
})

thirdTieCheck.addEventListener("change", function() {
    if (thirdTieCheck.checked) {
        thirdTiebreak.style.display = "";
    } else {
        thirdTiebreak.style.display = "none";
        thirdTieWinner.value = "None";
        thirdTieLoser.value = "None";
    }
})