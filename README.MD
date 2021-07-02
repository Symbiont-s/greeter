<div class="text-justify">

### Greeter

The GREETER is a Discord bot that was mainly built to assist Steem CMs/users/POs with their curation efforts and team management. 

### Requeriments
* Steem Beem library;
* TinyDb as a DB;
* Python3;
* Screen;
* and python3-venv.

### Instalation Instrunctions

### Discord Bot

Since it is a Discord bot, you need to create a discord bot and get your secret key. In order to do that, you can follow the below instructions:<sup>([1](https://www.freecodecamp.org/news/create-a-discord-bot-with-python/))</sp>

* _Make sure you’re logged on to the [Discord website](https://discord.com/)._

* _Navigate to the [application page](https://discord.com/developers/applications)._

* _Click on the “New Application” button._

<p align="center">
  <img width="460" height="300" src="https://user-images.githubusercontent.com/6106483/123680648-dd76f780-d840-11eb-9c9a-3d8abdf559c8.png">
</p>


* _Give the application a name and click “Create”._

<p align="center">
  <img width="500" height="500" src="https://user-images.githubusercontent.com/6106483/123681040-3a72ad80-d841-11eb-932c-98b449e46edd.png">
</p>
 
* _Go to the “Bot” tab and then click “Add Bot”. You will have to confirm by clicking "Yes, do it!"_
<p align="center">
  <img src="https://user-images.githubusercontent.com/6106483/123681074-4494ac00-d841-11eb-8c9d-48a56042879c.png">
</p>

* _Keep the default settings for Public Bot (checked) and Require OAuth2 Code Grant (unchecked). Your bot has been created. The next step is to copy the token._
<p align="center">
  <img src="https://user-images.githubusercontent.com/6106483/123681193-6d1ca600-d841-11eb-8b0a-89e814cdbf1e.png">
</p>

_This token is your bot's password so don't share it with anybody. It could allow someone to log in to your bot and do all sorts of bad things. You can regenerate the token if it accidentally gets shared._

* _Now you have to get your Bot User into a server. To do this, you should create an invite URL for it. Go to the "OAuth2" tab. Then select "bot" under the "scopes" section._
  
<p align="center">
  <img src="https://user-images.githubusercontent.com/6106483/123681455-c7b60200-d841-11eb-981c-7fdb0bbf98dd.png">
</p>
  
* _Now choose the permissions you want for the bot. Our bot is going to mainly use text messages so we don't need a lot of the permissions. You may need more depending on what you want your bot to do. Be careful with the "Administrator" permission._
  
<p align="center">
  <img src="https://user-images.githubusercontent.com/6106483/123681505-d3092d80-d841-11eb-99f0-ae1797df78dc.png">
</p>
  
_After selecting the appropriate permissions, click the 'copy' button above the permissions. That will copy a URL that can be used to add the bot to a server._

_Paste the URL into your browser, choose a server to invite the bot to, and click “Authorize”._

_To add the bot, your account needs "Manage Server" permissions._

### Setting Files & Bot Start

Now that your bot is ready, you need to take care of the installation of the bot files, settings, and all its dependencies on your Linux server:

* You need to install the proper Python system packages to run the bot on your server by doing:

```
sudo apt update && sudo apt install python3 python3-venv screen
```

* Then clone this repo by doing:

``` 
git clone https://github.com/Symbiont-s/greeter
```

* Navigate to the greeter folder and edit the file **settingsDiscordBot.py'** with the needed data (accounts, keys, voting power, delay, Discord key ...).
* Ater populating **'settingsDiscordBot.py'** with the proper data, you can proceed to start the bot and install the dependencies.
* Now, you’re going to use a tool called screen to create a virtual terminal. Without this tool, if you were to exit your terminal while the bot was running, the process would terminate, and your bot would go offline. With this tool, you can connect and disconnect to sessions so your code remains running. So first we are going to start a screen session with the name greeter (can be any name):

```
screen -S your_session_name
```

* Inside your screen session, just navigate to your greeter folder:

```
cd greeter
```

* Now, we are going to install the dependencies and environment by doping:

```
pip install pipenv
```
(You must have python installed previously)

```
pipenv install
```

Then Create the virtual environment and install the dependencies:

```
pipenv shell
```

* Finally, you can run your bot by doing:

```
python3 discordbot.py
```

### Stop & Exit & Restart

* To stop the bot inside the screen session, do:

```
CTRL+C
```

* To leave (detach) the screen session and keep the bot running in the background, do:

```
CTRL+A+D
```

* To reconnect (reattach) to the screen session, do:

```
screen -r greeter
```

* If you did not give a specific name to your screen session, you can list the list of screen sessions, then connect to the right one by doing:

```
screen -ls
```

```
screen -r ID_of_the_session
```

* To stop the bot completely, once inside the screen we can stop the bot running by pressing CTRL + C. Then with the command ```exit``` we exit the virtual environment and executing again ```exit``` we exit the screen and close it.

### Commands

The bot listens to several commands that are used for each specific Discord channel. The names of these channels need to match the names stored in settingsDiscordBot.py (``list_chanel``).

* **In the #curation-feed channel, the command that can be used is:**

**["!vote"]**

```
!vote [link] [weigth] - is used to send post links from the Steem blockchain to be upvoted with a specific weight percentage. eg:

!vote https://steemit.com/steem/@symbionts/postrul 100
```

* **In the #bot-hq channel, the commands that can be used are:**

**["!status","!hours","!power","!postvalue","!config","!delegate","!delegatees","!powerup"]**

```
!delegate [account] [amount] [accounts] - is used to delegate SP to other accounts using one of the `delegate_account_list` accounts, eg:

!delegate account_steem_1 30 account1,account2
!delegate account_steem_2 30 account1,account2

To remove delegation in Bulk change the value to 0, e.g:

!delegate account_steem_1 0 account1,account2
!delegate account_steem_2 0 account1,account2
```

```
!delegatees or !delegatees [account] - is used to get a general list of accounts you delegated to or with a specific account. eg:

!delegatees

or

!delegatees account_name
```

```
!delegatees details - is used to get all accounts to which SP was delegated with any of the `delegate_account_list` and the delegated amount
```

```
!delegatees [account] details - is used to returns all accounts to which SP was delegated with account_name and the delegated amount
```

```
!register [Discord ID] [Steem Account] - is used to bind a discord account to a Steem account. eg:

!register 328308281510723594 symbionts
```

```
!status - is used to get useful data that the bot has stored such as users that are in the delay window.
```

```
!hours [number] - is used to set the delay for authors to able to be voted again. eg:

!hours 24
```

```
!power [number] - is used to set the min VP for the vote requests to pass. eg:

!power 80
```

```
!postvalue [number] - is used to set the minimum post value for the vote requests to be accepted. eg:

!postvalue 10
```

```
!config - is used to get the current config that is being used.
```

```
!powerup [account] [amount_STEEM] [accounts] - is used to power up x STEEM of one of the accounts of `delegate_account_list` to a target account. eg:

!powerup account_name 1 user1,user2,user3
```
* **The channel #create-accounts channel allows you to create Steem accounts using create_claimed_account or create_account. To enable the option to create accounts you need to fill in the dictionary "account_creation_settings" that is in the "settingsDiscordBot.py" file.**

```
self.account_creation_settings = {
                "create_claimed_account":False,
                "create_account":True,
                "creator":"symbionts",
                "active_key":""
}
```
Since there are two ways to create Steem accounts, both options were placed so that it is easy to choose the one that suits you the best.

If "create_claimed_account" and "create_account" are set to True, then the bot will listen to the following commands:

```
!createRC accoun_tname - is used to create an account with Resource Credits (tickets)

and

!createSTEEM account_name - is used to create an account paying with STEEM (currently 3 STEEM - an amount set by witnesses)
```

If only one of the 2 was set as True, then the bot will listen to:

```
!create account_name
```

In case "create_claimed_account" has been set to True and "create_account" to False, then the account will be created with the RC ticket.

If on the other hand, "create_account" is set as True and "create_claimed_account" as False, then the account will be created by paying with STEEM.

**The accounts created and their private passwords will be stored in a .json file inside the greeter folder.**

`Note: If both are set to False then the bot does nothing`

* **In the #blacklist channel, the commands that can be used are:**

**["!blacklist","!remove"]**

```
!blacklist [name] [reason] - is used to add users to the blacklist. e.g:

!blacklist symbionts
```
```
!remove [name] - is used to remove users from the blacklist. e.g:

!remove symbionts
```
### Contribution & Features Request

The project is open for contributions and features requests.

For inquiries and discussion: https://discord.gg/Hf7saBFrn4

### Referances

1. https://www.freecodecamp.org/news/create-a-discord-bot-with-python (29/06/2021)

### License

GNU GENERAL PUBLIC LICENSE Version 3.

Brought to you by the Symbionts Team.
