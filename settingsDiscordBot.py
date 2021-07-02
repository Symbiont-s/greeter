'''
        The settings file for the bot.
'''

class Config:

    def __init__(self):

        #discord bot token
        self.botToken = ""
        
        #The cooldown period in hours, the value of this variable must be an integer greater than or equal to 0
        self.hours = 24

        #dictionary for account creation
        #create_claimed_account: Boolean value to enable account creation through Resource Credits
        #create_account: Boolean value to enable account creation through payment in STEEM
        #creator: account name that will be used to create new accounts
        #active_key: active account key that will be used to create new accounts
        self.account_creation_settings = {
                "create_claimed_account":False,
                "create_account":True,
                "creator":"symbionts",
                "active_key":""
        }

        #Steem account(s) that must meet the minimum voting power rule
        self.main_voting_account = [""]

        #The Steem account that will leave comments
        self.account_comment_STEEM = ''

        #Posting key of Steem account that will leave comments (Posting key)
        self.key_account_comment_STEEM = ''

        #A list of Steem accounts that will vote for the posts
        self.list_account_STEEM = ["account_1","account_2"]

        #A list of Steem accounts posting keys that will vote for posts (Posting key)
        self.keys_steem = ['post_key_account_1','post_key_account_2']

        #Names of the accounts that will be used to delegate and power up
        self.delegate_account_list = [""]
        #Active keys of the accounts that will be used to delegate and power up
        self.delegate_account_key_list = [""]

        #the minimum voting power for steem
        self.minimum_voting_power_steem = 80

        #A list of Steem accounts to claim their reward balance 
        self.list_accounts_crb_STEEM = ['']
        #A list of Steem accounts posting keys to claim their reward balance (Posting key)
        self.list_keys_accounts_crb_STEEM = ['']

        #A list of Steem accounts that will claim discounted accounts
        self.list_accounts_claim_account = ['']
        #A list of Steem accounts active keys to claim accounts (Active key)
        self.list_keys_accounts_claim_account = ['']

        #A list of the 4 discord channels that the bot will listen to, 
        #1-curation-feed-STEEM (vote for post)
        #2-bots-hq (account status who have voted within the cooldown period and others things)
        #3-create-accounts (Create new accounts for steem)
        #4-blacklist (add or remove users to blacklist)
        self.list_channel = ["curation-feed","bot-hq","create-accounts","blacklist"]

        #The commands that the bot will listen to, (these commands must be strings without spaces)
        #1-!vote command of the first channel in list_channel (vote for post)
        #2-!register command of the second channel in list_channel (associate the id of a discord user with a steem account)
        #3-!status command of the second channel in list_channel (List of accounts that have been voted on and have not yet reached the cooldown period)
        #4-!hours command of the second channel in list_channel (To set the hours delay.)
        #5-!power command of the second channel in list_channel (To set the minimum power.)
        #6-!postvalue command of the second channel in list_channel (To set the minimum post value to vote.)
        #7-!config command of the second channel in list_channel (View current settings)
        #8-!powerup command of the second channel in list_channel (power up other accounts with STEEM from an account in delegate_account_list)
        self.command = ["!vote","!register","!status","!hours","!power","!postvalue","!config","!powerup"]

        #The commands that the bot will listen to, (these commands must be strings without spaces)
        #1-!delegate command of the second channel in list_channel (Delegate SP to other accounts)
        #2-!delegatees command of the second channel in list_channel (view the list of accounts that have been delegated with the bot)
        self.command_delegate = ["!delegate","!delegatees"]
        
        #The commands that the bot will listen to, (these commands must be strings without spaces)
        #1-!blacklist command of the fourth channel in list_channel (add users to blacklist)
        #2-!remove command of the fourth channel in list_channel (remove users to blacklist)
        self.command_blacklist = ["!blacklist","!remove"]

        #Steem RPC nodes
        self.list_nodes =["",""]

        #Name That TinyDB will use for the STEEM DB that stores the info of the voted posts, the name must end with the extension .json
        self.db = 'db.json'

        #Name That TinyDB will use for the STEEM blacklist DB that stores the info of the voted posts, the name must end with the extension .json
        self.bldb = 'bldb.json'

        #Name That TinyDB will use to store the id of the Discord users and the name of their accounts in steem
        self.registered_accounts = "register.json"

        #Comment that can be posted on Steemit after voting for the post
        self.cmnts = """Hi, @%s,

Your post has been supported by @%s from the X.

Thank you for your contribution,"""

        #Comment that can be posted on Steemit after voting for the post,if the user has not registered their steem account on Discord
        self.cmnts_no_register = """Hi, @%s,

Your post has been supported by the X.

Thank you for your contribution,"""

        #STU limit from which a post will not be voted on (can be an integer number or with decimals)
        self.reward_limit_STEEM = 10  
        
        #Channel ID where the claim reward balances information will be displayed.
        self.id_channel_discord = 701202933693546546
# EOF
