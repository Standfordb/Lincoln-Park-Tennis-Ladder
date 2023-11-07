# All constants to be used by program
#
#

CHALLENGE_SPREAD = 3
RESULTS_PER_PAGE = 25
TIMESTAMP_FULL = "%m-%d-%Y %I:%M %p"
TIMESTAMP_DATE_ONLY = "%m-%d-%Y"

NOTIFICATIONS = {
    "CHALLENGE": "You have been challenged by",
    "CHALLENGE DECLINED": "Your challenge has been declined by",
    "CHALLENGE ACCEPTED": "Your challenge has been accepted by",
    "CHALLENGE CANCELED": "Your challenge match has been canceled by",
    "MESSAGE": "You have been messaged by",
    "MATCH REPORTED": "Your match results have been input by",
    "MATCH CONFIRMED": "Your match results have been confirmed by",
    "DISPUTE": "Your match results have been disputed by"
}

FRIENDLY = "FRIENDLY"
CHALLENGE = "CHALLENGE"
CHALL_DECLINED = "CHALLENGE DECLINED"
CHALL_ACCEPTED = "CHALLENGE ACCEPTED"
MESSAGE = "MESSAGE"
MATCH_REPORTED = "MATCH REPORTED"
MATCH_CONFIRMED = "MATCH CONFIRMED"
CHALL_CANCEL = "CHALLENGE CANCELED"
DISPUTE = "DISPUTE"

EMAIL_TITLE = {
    "CHALLENGE": "You have been challenged!",
    "RESULTS": "Your match results have been input!",
    "CANCELED": "Your challenge match has been canceled!"
}

EMAIL_BODY = {
    "CHALLENGE": "You have been challenged to a match on the Lincoln Park Tennis Ladder! Please head over to LPTennisLadder.com to accept this challenge. Play your best and have fun!",
    "RESULTS": "Your recent match results have been input by your opponent. Please head over to LPTennisLadder.com to confirm these results. Thank you!",
    "CANCELED": "Your challenge match has been cancelled by your opponent. Please reach out to them if you feel this has been done in error."
}