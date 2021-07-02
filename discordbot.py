# Python modules
import os
import random
import re
import time
import traceback
from datetime import datetime, timedelta,timezone

# Third Party Libraries
from beem.account import Account
from beem.comment import Comment
from beem.exceptions import AccountDoesNotExistsException,ContentDoesNotExistsException,AccountExistsException
from beem.rc import RC
from beem import Steem
from beemapi.exceptions import UnhandledRPCError
from beembase import operations
from beemgraphenebase.account import PasswordKey
import discord
from discord.ext import tasks
from tinydb import TinyDB, Query

# Own modules
import exceptions
import settingsDiscordBot

# Variables
client = discord.Client()
User = Query()
news_accounts_db = TinyDB("newAcountsdb.json")
commands_create_new_account = ["!create", "!createRC", "!createSTEEM"]
error = TinyDB("exceptions.json")

# Set the settings in the settingsDiscordBot.py file
cfg = settingsDiscordBot.Config()
minimum_voting_power = cfg.minimum_voting_power_steem
reward_limit = cfg.reward_limit_STEEM
main_voting_account = cfg.main_voting_account
hours = cfg.hours
account_creation_settings = cfg.account_creation_settings
command = cfg.command
command_delegate = cfg.command_delegate
command_blacklist = cfg.command_blacklist
list_channel = cfg.list_channel
delegate_account_list = cfg.delegate_account_list

# Steem settings
nodelist = cfg.list_nodes
s = Steem(node=nodelist, keys=cfg.keys_steem)

# DB
db = TinyDB(cfg.db)
bldb = TinyDB(cfg.bldb)
rgt_acc = TinyDB(cfg.registered_accounts)

# Set exceptions.py
excpt = exceptions.Exception_Handling()

# The Account_class class was created to override the transfer_to_vesting 
# method of the Acoount class from the Beem library
def extract_account_name(account):
    if isinstance(account, str):
        return account
    elif isinstance(account, Account):
        return account["name"]
    elif isinstance(account, dict) and "name" in account:
        return account["name"]
    else:
        return ""

class Account_class(Account):
        
    def transfer_to_vesting(self, amount, to=None, account=None, skip_account_check=False, **kwargs):
        """ Vest STEEM
            :param float amount: Amount to transfer
            :param str to: Recipient (optional) if not set equal to account
            :param str account: (optional) the source account for the transfer
                if not ``default_account``
            :param bool skip_account_check: (optional) When True, the receiver
                account name is not checked to speed up sending multiple transfers in a row
        """
        if account is None:
            account = self
        elif not skip_account_check:
            account = Account(account, blockchain_instance=self.blockchain)
        amount = self._check_amount(amount, self.blockchain.token_symbol)
        if to is None and skip_account_check:
            to = self["name"]  # powerup on the same accoun
        if not skip_account_check:
            to = Account(to, blockchain_instance=self.blockchain)
        to_name = extract_account_name(to)
        account_name = extract_account_name(account)           

        op = operations.Transfer_to_vesting(**{
            "from": account_name,
            "to": to_name,
            "amount": amount,
            "prefix": self.blockchain.prefix,
            "json_str": not bool(self.blockchain.config["use_condenser"]),
        })
        return self.blockchain.finalizeOp(op, account, "active", **kwargs)


async def exception_handling(e,funcion,dict_exceptions,channel=None):
    '''
    Check if the exception was presented before to verify if it should print a custom message stored 
    in the exception.py file and if it is the first time it is presented, the exception, its traceback 
    and the place where it is saved in the exception.json file was presented
            :param Exception e: The exception.
            :param str funcion: name of the function where it was presented.
            :params channel: discord channel where a message will be sent to warn of the error.
    '''
    if e is not None:
        if str(e) in dict_exceptions.keys():
            if dict_exceptions[str(e)] !="":
                await channel.send(dict_exceptions[str(e)])
        else:
            check = error.search((User.name == funcion) & (User.error == str(e)))
            await channel.send("Error: %s"%(str(e)))
            if check == []:
                error.insert({'name':funcion,'error':str(e),'traceback':str(traceback.format_exc())})
    else:
        if funcion == "create_account":
            await channel.send("An account with that name already exists")
        else:
            check = error.search((User.name == funcion) & (User.error == "empty"))
            await channel.send("Error")
            if check == []:
                error.insert({'name':funcion,'error':"empty",'traceback':str(traceback.format_exc())})


def validatehour(hour):
    '''
    Allows you to validate that the "hours" entered is an integer
    greater than or equal to 0 otherwise "hours" is equal to 1
            :param str-float-int hour: The number to validate
    '''
    global hours
    try:
        hours = int(hour)
        if(hours < 0):
            hours = 1
    except Exception as e:
        hours = 1
        if e is not None:
            if str(e) in excpt.validatehour.keys():
                print(excpt.validatehour[str(e)])
            else:
                check = error.search((User.name == "validatehour") & (User.error == str(e)))
                if check == []:
                    error.insert({'name':"validatehour",'error':str(e)})
        else:
            check = error.search((User.name == "validatehour") & (User.error == "empty"))
            if check == []:
                error.insert({'name':"validatehour",'error':"empty"})


def cal_slice(list_db):
    '''
    calculates how many pieces a list should be divided into so that at least the first of the pieces 
    has a length less than or equal to 1800 characters
            :param list list_db: a list
    '''
    div = 1
    character_length = len(str(list_db))
    while character_length > 1800:
        div=div*2
        character_length = len(str(list_db[0:int(len(list_db)/div)]))
    return div


async def send_slice_msg(parts,list_db,msg):
    '''
    send messages, cutting the content of a list into parts
            :param int list_db: parts into which the list will be divided
            :param list list_db: a list
            :param msg: discord channel
    '''
    star=0
    end=int(len(list_db)/parts)
    for i in range(0,parts):
        if end >= len(list_db):
            end=len(list_db)
            if(star>len(list_db)):
                break
        if len(str(list_db[star:end]))<1800:
            if list_db[star:end] != []:
                await msg.send("%s" % (str(list_db[star:end]).replace("},", "}\n")))
        else:
            await send_slice_msg(int(cal_slice(list_db[star:end])),list_db[star:end],msg)
        star=int(end)
        end=end*2


async def create_account(props, msg, **kwargs):
    '''
    Allows you to create a Steem account using create_claimed_account or create_account
    :param list props: message sent by discord channel separated in a list for each space
    :param obj msg: instance that allows interacting with discord
    :params **kmargs:
        :param bool create_claimed_account: Boolean value to enable account creation through Resource Credits
        :param bool create_account: Boolean value to enable account creation through payment in STEEM
        :param str creator: account name that will be used to create new accounts
        :param str active_key: active account key that will be used to create new accounts
    '''
    create_claimed_account = kwargs.get("create_claimed_account", False)
    create_account = kwargs.get("create_account", False)
    if create_claimed_account or create_account:
        creator = kwargs.get("creator", "")
        creator_active_key = kwargs.get("active_key", "")
        # Check if the name is valid
        account_name = props[1]
        pattern = re.compile(
            "^[a-z](-[a-z0-9](-[a-z0-9])*)?(-[a-z0-9]|[a-z0-9])*(?:\.[a-z](-[a-z0-9](-[a-z0-9])*)?(-[a-z0-9]|[a-z0-9])*)*$")
        valid = pattern.search(account_name)
        if valid:
            try:
                # Generate password
                longitud = 52
                valores = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
                p = ""
                p = p.join([random.choice(valores) for i in range(longitud)])
                news_accounts_db.insert({'account_name': account_name, 'master_password': p,
                                        'active': "", 'owner': "", 'posting': "", 'memo': "", 'status': "pending"})
                s_account = Steem(
                    node=nodelist, keys=creator_active_key)
                # Create account
                if create_claimed_account and create_account:
                    if props[0] == "!createRC":
                        password = s_account.create_claimed_account(
                            account_name=account_name, creator=creator, password=p)
                    if props[0] == "!createSTEEM":
                        password = s_account.create_account(
                            account_name=account_name, creator=creator, password=p)
                elif create_claimed_account and props[0] == "!create":
                    password = s_account.create_claimed_account(
                        account_name=account_name, creator=creator, password=p)
                elif create_account and props[0] == "!create":
                    password = s_account.create_account(
                        account_name=account_name, creator=creator, password=p)
                else:
                    raise ValueError("Wrong format")
                news_accounts_db.update(
                    {'status': "complete"}, User.account_name == account_name and User.status == "pending")
                k = ["active", "owner", "posting", "memo"]
                keys = [PasswordKey(account_name, p, role=i,
                                    prefix="STM") for i in k]
                await msg.channel.send("Account created.")
                await msg.channel.send("Master Password: %s" % (str(p)))
                for i in range(0, len(k)):
                    news_accounts_db.update({k[i]: str(keys[i].get_private(
                    ))}, User.account_name == account_name and User.status == "complete")
                    await msg.channel.send("%s keys" % (str(k[i])))
                    await msg.channel.send("private key: %s" % (str(keys[i].get_private())))
                    await msg.channel.send("public key: %s " % (str(keys[i].get_public())))
            except AccountExistsException:
                news_accounts_db.remove((User.account_name==account_name) & (User.status=="pending"))
                await msg.channel.send("An account with that name already exists")
            except UnhandledRPCError as enough:
                news_accounts_db.remove((User.account_name==account_name) & (User.status=="pending"))
                if enough is None:
                    dict_exceptions = excpt.create_account
                    await exception_handling(enough,"create_account",dict_exceptions,channel= msg.channel)
                else:
                    msg_error = str(enough)
                    if msg_error.find("has no claimed accounts to create")!=-1:
                        await msg.channel.send("You haven't claimed accounts to create")
                    elif msg_error.find("does not have sufficient funds for balance adjustment")!=-1:
                        await msg.channel.send("You don't have sufficient funds for create account")
                    else:
                        dict_exceptions = excpt.create_account
                        await exception_handling(enough,"create_account",dict_exceptions,channel= msg.channel)
            except Exception as error_create:
                news_accounts_db.remove((User.account_name==account_name) & (User.status=="pending"))
                dict_exceptions = excpt.create_account
                await exception_handling(error_create,"create_account",dict_exceptions,channel= msg.channel)
        else:
            await msg.channel.send("The account name is invalid")


async def delegate(props, msg):
    '''
    Delegates an amount of SP to multiple accounts.
    One of the accounts placed in delegate_account_list in the settingsDiscordBot.py file is used to delegate 
    an amount of steem present in the command to all valid accounts of the command.
            :param list props: command stored in a list where each item is a part of the command.
            :param Channel msg: Channel object of the channel class of discord
    '''
    if len(props)>=3:
        count=0
        try:
            list_accounts =[i for i in "".join(props[3::]).replace(" ","").split(",") if i]
            sp_required = int(props[2])*len(list_accounts)
            st_ins = Steem(node=nodelist, keys=cfg.delegate_account_key_list)
            name = props[1].casefold()
            if name in delegate_account_list:
                acc = Account(name, steem_instance=st_ins)
                if float(acc.sp) >= sp_required:
                    for account in list_accounts:
                        if str(name) != account:
                            amount = st_ins.sp_to_vests(float(props[2]))
                            acc.delegate_vesting_shares(account,amount)
                            count+=1
                        else:
                            await msg.channel.send("You cannot delegate SP to the same account you use to delegate")
                    await msg.channel.send("%i SP was delegated to %i accounts"%(int(props[2]),count))
                else:
                    await msg.channel.send("Not enough SP to delegate, current SP is %s SP and %s SP is needed to delegate %i SP to %i accounts" 
                    % (str(round(acc.sp,2)),str(sp_required-round(acc.sp,2)),int(props[2]),len(list_accounts)))
            else:
                await msg.channel.send("The %s account is not in the list of delegate accounts."%(name))
        except ValueError:
            await msg.channel.send("Invalid command")
        except AccountDoesNotExistsException as valError:
            await msg.channel.send("Account %s does not exist or is an invalid name"%(str(valError)))
            await msg.channel.send("%s SP was delegated to %s accounts and %s accounts could not be delegated"
            %((props[2]),count,len(list_accounts)-count))
            if len(str(list_accounts[count:len(list_accounts)]))<=1800:
                await msg.channel.send("The accounts that could not be delegated are the following: %s" %(",".join(list_accounts[count:len(list_accounts)])))
        except Exception as e:
            await msg.channel.send("%s SP was delegated to %s accounts and %s accounts could not be delegated"
            %((props[2]),count,len(list_accounts)-count))
            if len(str(list_accounts[count:len(list_accounts)]))<=1800:
                await msg.channel.send("The accounts that could not be delegated are the following: %s" %(",".join(list_accounts[count:len(list_accounts)])))
            dict_exceptions = excpt.delegate
            await exception_handling(e,"delegate",dict_exceptions,channel= msg.channel)
    else:
        await msg.channel.send("Invalid command")


async def list_delegatees(props, msg):
    '''
    Returns a list of all accounts that have been delegated SP.
            :param list props: command stored in a list where each item is a part of the command.
            :param Channel msg: Channel object of the channel class of discord
    '''
    try:
        st_ins = Steem(node=nodelist, keys=cfg.delegate_account_key_list)
        d_a_l = delegate_account_list
        #Helper to access sections of the command
        aux =["",""]
        #length of the list containing the command
        length = len(props)
        if length > 1:
            d_a_l = [props[1]] if props[1] in delegate_account_list else delegate_account_list
            aux[0] = props[1]
            if length == 3:
                aux[1] = props[2]
        if len(d_a_l)==1 or (d_a_l == delegate_account_list and (length==1 or (length==2 and aux[0]=="details"))):
            for account_name in d_a_l:
                acc = Account(account_name, steem_instance=st_ins)
                delegatees = acc.get_vesting_delegations()
                if delegatees == []:
                    await msg.channel.send("There are no accounts to display")
                else:
                    if length==1 or (length==2 and aux[0]==account_name):
                        list_accounts = [value["delegatee"] for value in delegatees]
                        if len(str(",".join(list_accounts)))>=1800:
                            await msg.channel.send("The account %s delegated to the following accounts:\n"%(account_name))
                            await send_slice_msg(cal_slice(list_accounts),list_accounts,msg.channel)
                        else:
                            await msg.channel.send("The account %s delegated to the following accounts:\n%s"
                            %(account_name,",".join(list_accounts)))
                    elif (length==2 and aux[0]=="details") or (length==3 and aux[1]=="details"):
                        list_accounts = []
                        for value in delegatees:
                            delegatees = {
                                "delegatee":value["delegatee"],
                                "SP":round(st_ins.vests_to_sp(float(value["vesting_shares"]["amount"])/(10**value["vesting_shares"]["precision"])),2),
                                "min_delegation_time":value["min_delegation_time"].replace("T"," T ")
                            }
                            list_accounts.append(delegatees)
                        if len(str(list_accounts))>=1800:
                            await msg.channel.send("The account %s delegated to the following accounts:\n"%(account_name))
                            await send_slice_msg(cal_slice(list_accounts),list_accounts,msg.channel)
                        else:
                            await msg.channel.send("The account %s delegated to the following accounts:\n%s"
                            %(account_name,str(list_accounts).replace("},", "}\n")))
                    else:
                        await msg.channel.send("invalid command")
        else:
            await msg.channel.send("invalid command")
    except Exception as e:
        dict_exceptions = excpt.list_delegatees
        await exception_handling(e,"list_delegatees",dict_exceptions,channel= msg.channel) 


async def power_up(props, msg):
    '''
    Power up a list of accounts with the steem of a main account
            :param list props: command stored in a list where each item is a part of the command.
            :param Channel msg: Channel object of the channel class of discord
    '''
    if len(props) >= 4:
        try:

            amount = float(props[2])
            if amount >= 0.001:
                count=0
                s_chain = Steem(node=nodelist, keys=cfg.delegate_account_key_list)
                name = props[1].casefold()
                if name in delegate_account_list:
                    acc_t = Account_class(name, steem_instance=s_chain)
                    list_accounts =[i for i in "".join(props[3::]).replace(" ","").split(",") if i]
                    steem_availables = float(str(acc_t.get_balances().get("available")[0]).replace(" STEEM",""))
                    if steem_availables >= len(list_accounts)*amount:
                        for account in list_accounts:
                            acc_t.transfer_to_vesting(amount = amount, to = account, account=name)
                            count+=1
                        await msg.channel.send("power up %.3f STEEM to %i accounts"%(float(props[2]),count))
                    else:
                        await msg.channel.send("Not enough STEEM.\n%.3f STEEM are needed to power up %.3f STEEM in %i accounts.\nYou currently have %.3f STEEM"
                        %(len(list_accounts)*amount, amount,len(list_accounts),steem_availables))
                else:
                    await msg.channel.send("The %s account is not in the list."%(name))
            else:
                await msg.channel.send("The second value of the command must be a number.")
        except ValueError as ve:
            await msg.channel.send("Invalid command.\nThe second value of the command must be a number. ")
        except AccountDoesNotExistsException as valError:
            await msg.channel.send("Account %s does not exist or is an invalid name"%(str(valError)))
            await msg.channel.send("power up %.3f STEEM power to the %i accounts, %i accounts could not power up"
            %(float(props[2]),count, len(list_accounts)-count))
            if len(str(list_accounts[count:len(list_accounts)]))<=1800:
                await msg.channel.send("The accounts that could not be power up are the following: %s" %(",".join(list_accounts[count:len(list_accounts)])))
        except Exception as exc:
            dict_exceptions = excpt.powerup 
            await exception_handling(exc,"powerup",dict_exceptions,channel= msg.channel)
    else:
        await msg.channel.send("Invalid command")


async def register(props, msg):
    '''
    Assign the id of a discord user a Steem account
            :param list props: command stored in a list where each item is a part of the command.
            :param Channel msg: Channel object of the channel class of discord
    '''
    if len(props) == 3:
        account_name = props[2]
        pattern = re.compile("^[a-z](-[a-z0-9](-[a-z0-9])*)?(-[a-z0-9]|[a-z0-9])*(?:\.[a-z](-[a-z0-9](-[a-z0-9])*)?(-[a-z0-9]|[a-z0-9])*)*$")
        valid = pattern.search(account_name)
        if valid:
            try:
                query_discord = rgt_acc.search(User.discordID == props[1])
                if(query_discord == []):
                    rgt_acc.insert({'discordID': props[1], 'account': account_name})
                    await msg.channel.send("%s has been associated with the account %s" % (props[1],account_name))
                else:
                    rgt_acc.update({'account': account_name}, User.discordID == props[1])
                    await msg.channel.send("%s has been associated with the account %s"% (props[1],account_name))
            except Exception as e:
                dict_exceptions = excpt.register
                await exception_handling(e,"register",dict_exceptions,channel= msg.channel)
        else:
            await msg.channel.send("The account name is invalid")


async def change_minimum_voting_power(props, msg):
    '''
    change minimum voting power
            :param list props: command stored in a list where each item is a part of the command.
            :param Channel msg: Channel object of the channel class of discord
    '''
    if len(props) == 2:
        global minimum_voting_power
        try:
            minimum_voting_power = float(props[1])
            if minimum_voting_power <= 0 or minimum_voting_power > 100:
                minimum_voting_power = cfg.minimum_voting_power_steem
                await msg.channel.send("Error, the minimum power must be a number greater than 0 and less than 100")
            else:
                await msg.channel.send("the minimum power was updated to %s"%(str(minimum_voting_power)))
        except Exception as e:
            minimum_voting_power = cfg.minimum_voting_power_steem
            await msg.channel.send("Error, invalid value")
            if e is not None:
                if not str(e) in excpt.change_minimum_voting_power.keys():
                    check = error.search((User.name == "change_minimum_voting_power") & (User.error == str(e)))
                    if check == []:
                        error.insert({'name':"change_minimum_voting_power",'error':str(e)})
            else:
                check = error.search((User.name == "change_minimum_voting_power") & (User.error == "empty"))
                if check == []:
                    error.insert({'name':"change_minimum_voting_power",'error':"empty"})


async def change_cooldown_period(props, msg):
    '''
    change cooldown period
            :param list props: command stored in a list where each item is a part of the command.
            :param Channel msg: Channel object of the channel class of discord
    '''
    global hours
    if len(props) == 2:
        hours = props[1]
        validatehour(hours)
        await msg.channel.send("The hours of delays were set to %s hours"%(str(hours)))


async def change_minimum_post_value(props, msg):
    '''
    change minimum post value
            :param list props: command stored in a list where each item is a part of the command.
            :param Channel msg: Channel object of the channel class of discord
    '''
    if len(props) == 2:
        global reward_limit
        try:
            reward_limit = float(props[1])
            if reward_limit <= 0:
                reward_limit = cfg.reward_limit_STEEM
                await msg.channel.send("Error, the minimum post value to vote must be a positive number")
            else:
                await msg.channel.send("The minimum post value to vote was updated to %s"%(str(reward_limit)))
        except Exception as e:
            reward_limit = cfg.reward_limit_STEEM
            dict_exceptions = excpt.change_minimum_post_value
            await exception_handling(e,"change_minimum_post_value",dict_exceptions,channel= msg.channel)

@client.event
async def on_ready():
    print("The bot is ready!")
    validatehour(hours)
    update.start()
    claim.start()
    claimacc.start()

@client.event
async def on_message(msg):
    if (msg.channel.name in list_channel and msg.author != client.user):
        props = msg.content.split()
        if ((props[0] == command[0]) and (msg.channel.name == list_channel[0])):
            try:
                query_discord = rgt_acc.search(User.discordID == str(msg.author.id))
                flags = [False,False,False]
                if(query_discord == []):
                    rgt_acc.insert({'discordID': str(msg.author.id), 'account': ""})
                else:
                    if(query_discord[0]["account"]!=""):
                        flags[0]=True 
                list_account = cfg.list_account_STEEM
                chain_acc_comment = Steem(
                    node=nodelist, keys=cfg.key_account_comment_STEEM)
                name = props[1].split("/")[4][1:]
                permlink = props[1].split("/")[5]
                query = db.search(User.name == name)
                if flags[0]:
                    cmnt = ""+cfg.cmnts%(name,query_discord[0]["account"])
                else:
                    cmnt = ""+ cfg.cmnts_no_register%(name)
                for account in main_voting_account:
                    acc_vote = Account(account, steem_instance=s)
                    if (acc_vote.get_voting_power() < minimum_voting_power):
                        flags[1]=True 
                        break
                rc = RC(steem_instance=chain_acc_comment)
                rc_cost = float(rc.comment(tx_size=len(cmnt),permlink_length=len("re-"+permlink+"-20210615t232938z"),parent_permlink_length=len(permlink)))
                for account in main_voting_account:
                    acc_main = Account(account, steem_instance=s)
                    rc_current = float(acc_main.get_rc()["rc_manabar"]["current_mana"])
                    if rc_cost*2.5 > rc_current:
                        flags[2]=True 
                        break
                querybl = bldb.search(User.name == name)
                if (querybl != []):
                    await msg.channel.send('%s is blacklisted' % (name))
                elif flags[1]:      
                    await msg.channel.send('Not enough voting power')
                elif flags[2]:      
                    await msg.channel.send('Not enough RC')
                elif (query == []) and (float(props[2])>0 and float(props[2])<=100):
                    weight = float(props[2])
                    P = Comment("@%s/%s" % (name, permlink),
                                    api="tags", blockchain_instance=s)
                    now = datetime.now(timezone.utc)
                    cond1 = now - P["created"]>timedelta(minutes=5)
                    cond2 = now < P["created"]+timedelta(days=6,hours=12)
                    current_reward = float(str(P.reward).split()[0])
                    if (not cond1):
                        await msg.channel.send('Sub 5 minutes upvote')
                    elif (not cond2):
                        await msg.channel.send('>12 hours before payout') 
                    elif current_reward >  reward_limit:
                        await msg.channel.send('The post is already generously rewarded.') 
                    else:
                        reply = Comment(
                            "@%s/%s" % (name, permlink), api="tags", blockchain_instance=chain_acc_comment)
                        for a in list_account:
                            P.upvote(weight, a)
                        now = datetime.now()
                        if not flags[0]:
                            await msg.channel.send('Your discord user does not have an associated steem account')      
                        reply.reply(cmnt, title="",
                                    author=cfg.account_comment_STEEM)
                        db.insert({'name':name,'post':props[1],'time':str(now)})
                        await msg.channel.send('Voting %s at %d by request from %s' % (name, weight,str(msg.author.mention)))
                elif (float(props[2])<0 or float(props[2])>100):
                    await msg.channel.send('the weight is invalid, enter a number between 1 and 100')
                else:
                    await msg.channel.send('%s was already upvoted in the last %d hours' % (name,hours))
            except ContentDoesNotExistsException:
                    await msg.channel.send('The link is invalid or the content does not exist')
            except Exception as e:
                dict_exceptions = excpt.curator_feed
                await exception_handling(e,"curator_feed",dict_exceptions,channel= msg.channel)
        if ((props[0] in command[1:8]) and (msg.channel.name == list_channel[1])):
            if props[0] == command[1]:
                await register(props,msg)
            elif props[0] == command[2]:
                try:
                    await msg.channel.send("Post voted within the cooldown period")
                    if len(str(db.all()))>=1800:
                        await send_slice_msg(cal_slice(db.all()),db.all(),msg.channel)
                    else:
                        await msg.channel.send("%s" % (str(db.all()).replace("},", "}\n")))
                    query_discord = rgt_acc.search(User.account != "")
                    await msg.channel.send("Discord users associated with a steem account")
                    if len(str(query_discord))>=1800:
                        await send_slice_msg(cal_slice(query_discord),query_discord,msg.channel)
                    else:
                        await msg.channel.send("%s" % (str(query_discord).replace("},", "}\n")))
                except Exception as e:
                    dict_exceptions = excpt.status
                    await exception_handling(e,"status",dict_exceptions,channel= msg.channel)
            elif props[0] == command[3]:
                await change_cooldown_period(props,msg)
            elif props[0] == command[4]:
                await change_minimum_voting_power(props,msg)
            elif props[0] == command[5]:    
                await change_minimum_post_value(props,msg)
            elif props[0] == command[6]:
                await msg.channel.send("The current settings are as follows")
                await msg.channel.send("    Minimum power to vote: %s"%(str(minimum_voting_power)))
                await msg.channel.send("    The cooldown period in hours: %s"%(str(hours)))
                await msg.channel.send("    The minimum post value to vote: %s"%(str(reward_limit)))
            elif props[0] == command[7]:
                await power_up(props,msg)
        if ((props[0] in command_delegate) and (msg.channel.name == list_channel[1])):   
            if props[0] == command_delegate[0]:
                await delegate(props,msg)
            elif props[0] == command_delegate[1]:
                if len(props) > 0 and len(props)<=3:
                    await list_delegatees(props,msg)
        if ((props[0] in commands_create_new_account) and (msg.channel.name == list_channel[2])):
            await create_account(props,msg, **account_creation_settings)
        if ((props[0] in command_blacklist) and (msg.channel.name==list_channel[3])):
            if(props[0] == command_blacklist[0]):
                try:
                    if len(props)==1:
                        if len(str(bldb.all()))>=1800:
                            await send_slice_msg(cal_slice(bldb.all()),bldb.all(),msg.channel)
                        else:
                            await msg.channel.send("%s" % (str(bldb.all()).replace("},", "}\n")))
                    elif len(props)>1:
                        querybl = bldb.search((User.name == props[1]))
                        if (querybl == []):
                            bldb.insert({'name':props[1],'reason':" ".join(props[2:])})
                            await msg.channel.send('User %s is now blacklisted'% props[1])
                        else:
                            await msg.channel.send('User %s is already blacklisted for %s' % (props[1],querybl[0]["reason"]))
                except Exception as e:
                    dict_exceptions = excpt.blacklist
                    await exception_handling(e,"blacklist",dict_exceptions,channel= msg.channel)
            elif(props[0] == command_blacklist[1]):
                try:
                    if len(props)==2:
                        querybl = bldb.search((User.name == props[1]))
                        if (querybl != []):
                            bldb.remove(User.name == props[1])
                            await msg.channel.send("The account %s was removed from the blacklist"%(props[1]))
                        else:
                            await msg.channel.send("The account %s was not in the blacklist"%(props[1]))
                except Exception as e:
                    dict_exceptions = excpt.blacklist
                    await exception_handling(e,"blacklist",dict_exceptions,channel= msg.channel)
        

@tasks.loop(minutes=5)
async def update():
    try:
        list_post = db.all()
        now =  datetime.now()
        for u in list_post:
            try:
                date = datetime.strptime(u["time"], '%Y-%m-%d %H:%M:%S.%f')
            except ValueError as ve:
                db.remove(User.name==u["name"])
                continue
            if now - date >= timedelta(hours=hours):
                db.remove(User.name==u["name"])
    except Exception as e:
        if e is not None:
            if str(e) in excpt.update.keys():
                print(excpt.update[str(e)])
            else:
                check = error.search((User.name == "update") & (User.error == str(e)))
                if check == []:
                    error.insert({'name':"update",'error':str(e),'traceback':str(traceback.format_exc())})
        else:
            check = error.search((User.name == "update") & (User.error == "empty"))
            if check == []:
                error.insert({'name':"update",'error':str(e),'traceback':str(traceback.format_exc())})

@tasks.loop(minutes=60)
async def claim():
    bchannel = client.get_channel(cfg.id_channel_discord)
    try:
        chain = Steem(node=nodelist,
                      keys=cfg.list_keys_accounts_crb_STEEM)
        list_account = cfg.list_accounts_crb_STEEM 
        for accountClaim in list_account:
            acc = Account(accountClaim, steem_instance=chain)
            rewards = acc.get_balances().get("rewards")
            try:
                acc.claim_reward_balance()
            except Exception as e:
                dict_exceptions = excpt.claim
                await exception_handling(e,"claim",dict_exceptions,channel= bchannel)  
            await bchannel.send('The account %s claimed %s \n' % (str(accountClaim), str(rewards)))
    except Exception as e:
        if e is not None:
            await bchannel.send("Error getting data %s"%(str(e)))
        else:
            dict_exceptions = excpt.claim
            await exception_handling(e,"claim",dict_exceptions,channel= bchannel)


@tasks.loop(minutes=480)
async def claimacc():
    bchannel = client.get_channel(cfg.id_channel_discord)
    try:
        list_account = cfg.list_accounts_claim_account
        ns = Steem(node=nodelist,
                   keys=cfg.list_keys_accounts_claim_account)
        for accountClaim in list_account:
            rc = RC(steem_instance=ns)
            cacc = Account(accountClaim, steem_instance=ns)
            current_costs = ns.get_rc_cost(rc.get_resource_count(
                tx_size=300, new_account_op_count=1, execution_time_count=1))
            current_mana = cacc.get_rc_manabar()["current_mana"]
            if (current_costs + 10 < current_mana):
                ns.claim_account(cacc)
                await bchannel.send("+1 discounted account claimed by the account %s." % (str(accountClaim)))
            else:
                await bchannel.send("Not enough RC for an account claim! in Account %s" % (str(accountClaim)))
    except Exception as e:
        dict_exceptions = excpt.claimacc 
        await exception_handling(e,"claimacc",dict_exceptions,channel= bchannel)

client.run(cfg.botToken)