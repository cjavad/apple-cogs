import re
import json
import math
import time
from datetime import datetime
from difflib import get_close_matches
import requests
from discord import Embed, Permissions
from redbot.core import commands

KEY = "2CD774287543683380F3E200E819F8D4"
GAME_ID = 730 # Default counter strike
SM_FORMAT = True # Forcing STEAM_1:X:X instead of STEAM_X:X:X
MAX_PLAYED_2_WEEKS = 168 # Amount of hours it's normal to play over 2 weeks

def get_reference_type(steam_reference):
    if re.match(r"STEAM_[0-1]:[0-1]:\d+", steam_reference):
        return "steamid"

    elif re.match(r"U:[0-9]:\d{1,20}", steam_reference.strip("[").strip("]")):
        return "steamid3"

    elif re.match(r"\d{17}", steam_reference):
        return "steamid64"
    else:
        return "customurl"

def clean_steam_reference(steam_reference):
    if "://" in steam_reference:
        sid_split = steam_reference.split("/")
        if steam_reference.endswith("/"):
            steam_reference = sid_split[:-1].pop()
        else:
            steam_reference = sid_split.pop()

        return steam_reference
    
    else:
        return steam_reference

def get_steamid_by_int64(steamid64):
  steamid = []
  steamid.append('STEAM_{}:'.format("1" if SM_FORMAT else "0"))
  steamidacct = int(steamid64) - 76561197960265728
  
  if steamidacct % 2 == 0:
      steamid.append('0:')
  else:
      steamid.append('1:')
  
  steamid.append(str(steamidacct // 2))
  
  return ''.join(steamid)

def get_int64_by_steamid(steamid):
  sid_split = steamid.split(':')
  steamid64 = int(sid_split[2]) * 2
  
  if sid_split[1] == '1':
      steamid64 += 1
  
  steamid64 += 76561197960265728
  return steamid64

def get_steamid3_by_int64(steamid64):
    steamid3 = []
    steamid3.append('[U:1:')
    steamidacct = int(steamid64) - 76561197960265728
    steamid3.append(str(steamidacct) + ']')
    
    return ''.join(steamid3)

def get_int64_by_steamid3(steamid3):
  for ch in ['[', ']']:
    if ch in steamid3:
      steamid3 = steamid3.replace(ch, '')
  
  steamid3_split = steamid3.split(':')
  steamid64 = int(steamid3_split[2]) + 76561197960265728
  
  return steamid64

def get_title_for_box(steam_reference, username):
    if get_reference_type(steam_reference) == "steamid":
        return steam_reference + " recognized as a STEAMID and found user " + username

    elif get_reference_type(steam_reference) == "steamid3":
        return steam_reference + " recognized as a STEAMID3 and found user " + username

    elif get_reference_type(steam_reference) == "steamid64":
        return steam_reference + " recognized as a STEAMID64 and found user " + username
    else:
        return steam_reference + " recognized as a customURL and found user " + username

def get_real_date(ts):
    return datetime.utcfromtimestamp(ts).strftime('%d-%m-%Y %H:%M:%S')

def get_profile_by_int64(int64):
    return json.loads(requests.get("https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={}&format=json&steamids={}".format(KEY, str(int64))).text)["response"]["players"][0]

def get_games_by_int64(int64):
    return json.loads(requests.get("https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={}&steamid={}&format=json".format(KEY, int64)).text)["response"]

def get_bans_by_int64(int64):
    return json.loads(requests.get("https://api.steampowered.com/ISteamUser/GetPlayerBans/v1/?key={}&format=json&steamids={}".format(KEY, str(int64))).text)["players"][0]

def get_int64_by_customurl(customurl):
    result = json.loads(requests.get("https://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={}&vanityurl={}".format(KEY, customurl)).text)["response"]
    return result["steamid"] if result["success"] == 1 else 0

def get_friends_by_int64(int64):
    friends = json.loads(requests.get("http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={}&steamid={}&relationship=friend".format(KEY, str(int64))).text)
    return friends["friendslist"]["friends"] if friends else []

def get_profile_by_steam(inp, isadmin = False):
    # clean steam reference (remove steamcommunity url)
    steam_reference = clean_steam_reference(inp)

    # Get type of steam reference (fx if it's a custom url use vanityurl to parse it)
    steam_reference_type = get_reference_type(steam_reference)

    # Set steamid as int
    steamid64 = int()
    
    # Logic switch that gets steamid64 based on type of steam reference
    if steam_reference_type == "customurl":
        steamid64 = get_int64_by_customurl(steam_reference)
    
    elif steam_reference_type == "steamid":
        steamid64 = get_int64_by_steamid(steam_reference)
    
    elif steam_reference_type == "steamid3":
        steamid64 = get_int64_by_steamid3(steam_reference)
    
    elif steam_reference_type == "steamid64":
        steamid64 = int(steam_reference)

    # STEAM API
    steam_api = get_profile_by_int64(steamid64)
    profile_link = steam_api["profileurl"]
    custom_url = profile_link.split("/")[:-1].pop() if "id" in profile_link else "None"
    created = get_real_date(steam_api["timecreated"]) if "timecreated" in steam_api.keys() else "None"
    communityvisibilitystate = steam_api["communityvisibilitystate"] - 2
    profilename = steam_api["personaname"] if "personaname" in steam_api.keys() else "None"
    lastlogoff = get_real_date(steam_api["lastlogoff"]) if "lastlogoff" in steam_api.keys() else "None"

    ret = {
        "steamid":get_steamid_by_int64(steamid64),
        "steamid3":get_steamid3_by_int64(steamid64),
        "steamid64":str(steamid64),
        "custom_url":custom_url,
        "profile_name":profilename,
        "visibility_state": "public" if communityvisibilitystate else "private",
        "profile_created":created,
        "status": (("Online" if steam_api["personastate"] == 1 else "Away") if steam_api["personastate"] else "Offline") if communityvisibilitystate else "None",
        "last_logoff":lastlogoff,
        "avatar":steam_api["avatarfull"]
    }

    

    # Calculate probabillity that the account is an alt (Admin Only)
    # Also means that multiple api requests are limited for admin use only
    if isadmin:
        # Get current time for calculating profile age, friend age and such.
        current_timestamp = time.time()

        # STEAM GAMES
        # Get all games, but get results for a game specificly if the profile is showing games
        games = get_games_by_int64(steamid64)

        # Get hours for focus game, in our case it's csgo.
        if "games" in games.keys():
             game = [game for game in games["games"] if game["appid"] == GAME_ID] if communityvisibilitystate else []
        else:
            game = [] # Games are hidden
            ret["visibility_state"] = "hidden"

        # If the account has game
        if len(game) == 1:
            # Check if the account has any hours in game (showing hours)
            if game[0]["playtime_forever"] != 0:
                # If so add the hours to the return table under game hours (convert into hours and floor)
                ret["game_hours"] = str(math.floor(game[0]["playtime_forever"] / 60)) + " hours"

                # If they have played in the last 2 weeks mark it down too.
                if "playtime_2weeks" in game[0].keys():
                    ret["last_2_weeks"] = str(math.floor(game[0]["playtime_2weeks"] / 60)) + " hours"
        
        # STEAM FRIENDS
        steam_friends = get_friends_by_int64(steamid64)
        amount_friends = len(steam_friends)

        # If friends are public add them to the output
        if communityvisibilitystate:
            ret["amount_of_friends"] = str(amount_friends) + " Friends"
            
        # Calculate a Trust-factor of sorts
        profile_trust = 0
        total_played = 0 # In days too
        average_played = 0 # Average amount of time player in days each year
        played_2weeks = 0 # Amount of hours played recently
        total_time_friended = 0 # In months (every 30 days i 1)
        average_time_friended = 0 # Average amount of months you have had a friend
        account_age = 0 # Account age in years too (way too influential other wise, also 1 month every 30 days)
        time_since_last_played = 0 # Amount of days since the profile was last online/logged in to

        # First the basics if the profile is not configured, then you automaticly lose a 100 points.
        profilestate = steam_api["profilestate"]

        # Find account age, if profile is private this will be 0.
        if profilestate and created != "None":
            account_age = math.floor((current_timestamp - steam_api["timecreated"])/60/60/24/30/12) # Convert to years

        # Start by getting total hours played on a steam profile
        if profilestate and "games" in games.keys():
            for game in games["games"]:
                total_played += math.floor(game["playtime_forever"] / 60 / 24)

                if "playtime_2weeks" in game.keys():
                    played_2weeks += math.floor(game["playtime_2weeks"] / 60)
            
            average_played = math.floor(total_played / account_age if account_age > 0 else 1)
        
        # Then get time friended in days
        if profilestate and amount_friends != 0:
            for friend in steam_friends:
                total_time_friended += math.floor((current_timestamp - friend["friend_since"])/60/60/24/30) # Convert to months
            
            average_time_friended = math.floor(total_time_friended / amount_friends)

        
        if played_2weeks > MAX_PLAYED_2_WEEKS:
            played_2weeks = 0 # Nulify those points
        
        if profilestate and lastlogoff != "None":
            time_since_last_played = math.floor((current_timestamp - steam_api["lastlogoff"])/60/60/24)

        # For now profile trust as a number, this is needed to collect data to make a interval and create
        # a dataset i can train to calculate a procentage.
        profile_trust = (average_played + average_time_friended + account_age + played_2weeks) - time_since_last_played

        ret["activity_score"] = str(profile_trust)


    # Add profile link last
    ret["profile_url"] = "https://steamcommunity.com/profiles/" + str(steamid64) + "/"

    return ret

def get_faceit_by_int64_or_nick(indentifier, extended = False):
    get_png_skill = lambda i: "https://eloboss.net/static/boost/ELO_{}.png".format(str(i)) if i in range(1, 11) else ""

    auth = {
        "accept":"application/json",
        "Authorization":"Bearer 1bd1709d-46a9-4d60-8aa3-08deb83e5ae7"
    }

    url = "https://open.faceit.com/data/v4/players?game=csgo&game_player_id=" + str(indentifier) if type(indentifier) == int or indentifier.isnumeric() else "https://open.faceit.com/data/v4/players?nickname={}&game=csgo".format(indentifier)
    res = json.loads(requests.get(url, headers=auth).text)

    # check if account exists
    if "player_id" in res.keys() and "csgo" in res["games"].keys():
        faceit = {
            "nickname":res["nickname"],
            "steamid64":res["games"]["csgo"]["game_player_id"],
            "avatar":res["avatar"] or "https://i.imgur.com/KmXNNl8.jpg",
            "region":res["games"]["csgo"]["region"],
            "skill_level":res["games"]["csgo"]["skill_level"],
            "skill_level_img":get_png_skill(int(res["games"]["csgo"]["skill_level"])),
            "elo":res["games"]["csgo"]["faceit_elo"]
        }
        
        # get more data yay!
        if extended:
            url_e = "https://open.faceit.com/data/v4/players/{}/stats/csgo".format(res["player_id"])
            res_e = json.loads(requests.get(url_e, headers=auth).text)
            if "lifetime" in res_e.keys():
                faceit.update(res_e["lifetime"])
                faceit["Recent Results"] = ', '.join(faceit["Recent Results"]).replace("0", "L").replace("1", "W")
                del faceit["Total Headshots %"]
                del faceit["K/D Ratio"]
        
        faceit["faceit_url"] = res["faceit_url"].replace("{lang}", "en")

        return faceit
    else:
        # account does not exist
        return False

# Classname should be CamelCase and the same spelling as the folder
class steam(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    """
    COG that provides the command [p]steam, that can parse steam input and return steam details.
    """

    @commands.command(pass_context=True)
    async def steam(self, ctx):
        """
        -steam [steam reference] (result only) -> Returns information on steam profile

        [steam reference] ie. steamID, steamID3, steamID64, a customURL or a full URL
        [result only] name of element to return ie. steamid or profile url (optional)

        Some valid examples:

        a steamID               	STEAM_0:0:11101
        a steamID3	                [U:1:22202]
        a steamID3 without brackets	U:1:22202
        a steamID64	                76561197960287930
        a customURL	                gabelogannewell
        a full URL	                https://steamcommunity.com/profiles/76561197960287930
        a full URL with customURL	https://steamcommunity.com/id/gabelogannewell
        """

        one_message = False
        result_only = None

        try:
            com = ctx.message.content.split(" ")
            steam_reference = ""
            is_admin = (ctx.message.author.permissions_in(ctx.message.channel).kick_members)

            if len(com) <= 1:
                if not one_message:
                    await ctx.message.channel.send("> No steam reference given.")
                    one_message = True

            elif len(com) == 2:
                steam_reference = com[1]
            
            elif len(com) >= 3:
                steam_reference = com[1]
                result_only = ' '.join(com[2:])

            # Clean steam reference here also, just to get the correct output later on.
            steam_reference = clean_steam_reference(steam_reference)

            result = get_profile_by_steam(steam_reference, is_admin if not result_only else False)
    
            if result:
                icon = result["avatar"]
                del result["avatar"]

                embed = Embed(color=0xFA8500)
                embed.set_author(name=get_title_for_box(steam_reference, result["profile_name"]), url=result["profile_url"], icon_url=icon)
                embed.set_footer(text="Results provided by Valve. Author: apple#0018")

                if not result_only:
                    for kn in result.keys():
                        if result[kn] != "None":
                            embed.add_field(name=kn.upper().replace("_", " "), value=result[kn])
                        else:
                            continue

                elif result_only:
                    opt = list(result.keys())
                    matches = get_close_matches(result_only, opt)
                    if len(matches) >= 1:
                        kn = matches[0]
                        # Make copy pastable on phone.
                        embed = Embed() # reset it
                        embed.title = result[kn] # make it only contain return element

                        if not one_message:
                            await ctx.message.channel.send(embed=embed)
                            one_message = True
                    else:
                        if not one_message:
                            await ctx.message.channel.send("> No such return as '" + result_only + "' in this search.")
                            one_message = True

                if not one_message:
                        await ctx.message.channel.send(embed=embed)
                        one_message = True
                
                # Using less-faceit for -steam also
                faceit = get_faceit_by_int64_or_nick(result["steamid64"])
                faceit_embed = Embed(color=0xFA8500)

                if faceit:
                    faceit_embed.set_author(name="Found faceit profile {} for steam {}".format(faceit["nickname"], steam_reference), icon_url=faceit["avatar"])
                    faceit_embed.set_thumbnail(url=faceit["skill_level_img"])
                    faceit_embed.add_field(name="SKILL LEVEL", value=faceit["skill_level"])
                    faceit_embed.add_field(name="ELO", value=faceit["elo"])
                    faceit_embed.add_field(name="REGION", value=faceit["region"])
                    faceit_embed.add_field(name="FACEIT URL", value=faceit["faceit_url"])
                    await ctx.message.channel.send(embed=faceit_embed)

                
                # CHECK FOR VAC BANS SEPERATE OF THE ONE MESSAGE LOOP
                # Check for vac bans
                bans = get_bans_by_int64(result["steamid64"])
                vac_embed = Embed()

                if bans["VACBanned"] or bans["NumberOfGameBans"]:
                    days_since_last = bans["DaysSinceLastBan"]
                    amount_of_vac = bans["NumberOfVACBans"]
                    amount_of_game = bans["NumberOfGameBans"]
                    vac_word = "ban" if amount_of_vac == 1 else "bans"
                    game_word = "ban" if amount_of_game == 1 else "bans"

                    if amount_of_game:
                        vac_embed.title = "WARNING {} has {} game {} on record! ".format(result["profile_name"], amount_of_game, game_word)
                        vac_embed.colour = 0xffff00

                    if bans["VACBanned"]:
                        vac_embed.title = "WARNING {} has {} VAC {}".format(result["profile_name"], amount_of_vac, vac_word) + (" and {} game {} on record!".format(amount_of_game, game_word) if amount_of_game else " on record!")
                        vac_embed.colour = 0xff0000

                    vac_embed.set_thumbnail(url="https://cdn2.iconfinder.com/data/icons/freecns-cumulus/32/519791-101_Warning-512.png")
                    
                    vac_embed.add_field(name="VAC bans", value=str(amount_of_vac), inline=True)
                    vac_embed.add_field(name="Game bans", value=str(amount_of_game), inline=True)
                    vac_embed.add_field(name="Days since last ban", value=str(days_since_last), inline=False)

                    await ctx.message.channel.send(embed=vac_embed)

            else:
                if not one_message:
                    await ctx.message.channel.send("> Steam reference could not be found.")
                    one_message = True

        except Exception as e:
            print(e)
            if not one_message:
                await ctx.message.channel.send("> Failed to load steam api. See console for error dump.")
                one_message = True
        
        await ctx.message.delete() # delete message when done

    @commands.command(pass_context=True)
    async def faceit(self, ctx):
        """
        -faceit [steam reference] -> Returns detailed information on faceit profile
        """

        one_message = False

        try:
            com = ctx.message.content.split(" ")
            steam_reference = ""

            if len(com) <= 1:
                if not one_message:
                    await ctx.message.channel.send("> No steam reference given.")
                    one_message = True

            else:
                steam_reference = com[1]
            

            # Clean steam reference here also, just to get the correct output later on.
            steam_reference = clean_steam_reference(steam_reference)

            steam_reference_type = get_reference_type(steam_reference)

            if steam_reference_type == "steamid64":
                steam_reference = int(steam_reference)
            elif steam_reference_type == "steamid":
                steam_reference = get_int64_by_steamid(steam_reference)
            elif steam_reference_type == "steamid3":
                steam_reference = get_int64_by_steamid3(steam_reference)
            else:
                steam_reference = steam_reference # assume it's a faceit nick

            result = get_faceit_by_int64_or_nick(steam_reference, True)

            if result:
                icon = result["avatar"]
                thumb = result["skill_level_img"]
                del result["avatar"]
                del result["skill_level_img"]

                embed = Embed(color=0xFA8500)
                embed.set_author(name="Found faceit profile {} for steam {}".format(result["nickname"], steam_reference), icon_url=icon)
                embed.set_footer(text="Results provided by Faceit. Author: apple#0018")
                embed.set_thumbnail(url=thumb)

                
                for kn in result.keys():
                    if result[kn]:
                        embed.add_field(name=kn.upper().replace("_", " "), value=result[kn])
                    else:
                        continue

                if not one_message:
                        await ctx.message.channel.send(embed=embed)
                        one_message = True

            else:
                if not one_message:
                    await ctx.message.channel.send("> Faceit profile could not be found.")
                    one_message = True

        except Exception as e:
            print(e)
            if not one_message:
                await ctx.message.channel.send("> Failed to load faceit api. See console for error dump.")
                one_message = True
        
        await ctx.message.delete() # delete message when done
