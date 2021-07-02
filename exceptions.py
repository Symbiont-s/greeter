'''
        A file to handle exceptions and responses

        The attributes of the Exception_Handling class represent a function of discordbot.py.

        Each attribute is a dictionary, where the keys are the errors and the values of those keys the responses that you want to print.
'''


class Exception_Handling:

    def __init__(self):

        self.curator_feed = {
            "Assert Exception:itr->vote_percent != o.weight: Your current vote on this comment is identical to this vote." : "I have already voted for this post with the same weight of the vote",
            "Assert Exception:(now - auth.last_post) >= STEEM_MIN_REPLY_INTERVAL_HF20: You may only comment once every 3 seconds." : "The post was voted but not commented, because the account made a comment 3 seconds ago.",
            "Assert Exception:( now - voter.last_vote_time ).to_seconds() >= STEEM_MIN_VOTE_INTERVAL_SEC: Can only vote once every 3 seconds." : "Only one post can be voted on every 3 seconds, please wait.",
            "list index out of range": "Wrong format"
        }
        self.status = {
            "list index out of range" : "invalid command",
            "400 Bad Request (error code: 50035): Invalid Form Body\nIn content: Must be 4000 or fewer in length.": "The message sent must be 4000 or fewer in length",
            "400 Bad Request (error code: 50035): Invalid Form Body\nIn content: Must be 2000 or fewer in length.": "The message sent must be 2000 or fewer in length.",
            
        }
        self.claim = {
            "Assert Exception:reward_steem.amount > 0 || reward_sbd.amount > 0 || reward_vests.amount > 0: Must claim something.":"",
            "list index out of range" : ""
        }
        self.claimacc = {
            " ": "-"
        }
        self.create_account = {
            "  ":"-"
        }
        self.validatehour = {
            "  ": "-"
        }
        self.change_minimum_voting_power = {
            "  ": "-"
        }
        self.register = {
            "  ": "-"
        }
        self.change_minimum_post_value = {
            "  ": "-"
        }
        self.delegate = {
            "  ": "-"
        }
        self.list_delegatees = {
            "  ": "-"
        }
        self.blacklist = {
            "list index out of range" : "invalid command"
        }
        self.update = {
            " ":"-"
        }
        self.powerup = {
            " ":"-"
        }