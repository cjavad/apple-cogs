from random import choice
from discord import Embed, Emoji
from redbot.core import commands

CSFIRE_RECOVER_URL = "https://support.steampowered.com/kb_article.php?ref=5421-QTFB-3090"

CSFIRE_SERVERS = {
    "meta":{
        "al":":flag_us: #{} CSFIRE 5v5 Competitive [AL] ",
        "ch":":flag_us: #{} CSFIRE 5v5 Competitive [CH] ",
        "ip":"steam://connect/{}"
    },
    "al":[
        "74.91.121.176:27015",
        "74.91.121.176:27025"
        ],
    "ch":[
        "162.248.88.144:27035",
        "162.248.88.144:27045"
    ]
}

CSFIRE_RULES = [
    {"name":"Rule 1", "value":"Speak only English via voice or text chat to maintain clear channels of communication."},
    {"name":"Rule 2", "value":"Do not Grief, Cheat, Script or Exploit. If found to be in breach of this rule, bans received will be **permanent** and **unappealable**. This applies to previous accounts which have been VAC banned and played on csfire."},
    {"name":"Rule 3", "value":"Do not impersonate any players or csfire Staff."},
    {"name":"Rule 4", "value":"No alternative accounts on csfire.\n\n **NOTE: In a rising trend on our servers, alternative accounts are frequently being used to throw, cheat, or evade previous bans, therefore, if caught using an alternative account, it will be permanently banned from the servers. Bans for this do not carry across accounts. Accounts with VAC / Game Bans received over 365 days ago are exempt from this rule.**"},
    {"name":"Rule 5", "value":"Do not abuse !calladmin. The feature is pivotal for moderating the servers and abuse of the system is dealt with promtly and bans will not be overturned."},
    {"name":"Rule 6", "value":"Advertisements of any kind are forbidden. Soliciting the sales of services (hacks, boosting, etc.), linking players to external sites (gambling, free skins etc), or the promotion of servers other than csfire.xyz is strictly prohibited."},
    {"name":"Rule 7", "value":"Treat other players with respect. Instances of malicious racism, sexism or homophobia are frowned upon and when found to be in breach of this rule, bans will progressively increase with each cumulative offence."},
    {"name":"Rule 8", "value":"Do not disrupt the server in any way. Acts of disruption can include, but are not limited to:\n\n - Mic/Chat spam\n - Trolling\n - Team flashing \n - Blocking\n - Ghosting\n - Shooting allies to reveal their position"}
]

CSFIRE_RANKS = [
    {"name":"Silver 1", "value":"100 Points", "key":"s1"},
    {"name":"Gold Nova 1", "value":"1050 Points", "key":"gn1"},
    {"name":"Master Guardian Elite", "value":"4750 Points", "key":"mge"},
    {"name":"Silver 2", "value":"250 Points", "key":"s2"},
    {"name":"Gold Nova 2", "value":"1350 Points", "key":"gn2"},
    {"name":"Distinguished Master Guardian", "value":"7550 Points", "key":"dmg"},
    {"name":"Silver 3", "value":"350 Points", "key":"s3"},
    {"name":"Gold Nova 3", "value":"1550 Points", "key":"gn3"},
    {"name":"Legendary Eagle", "value":"8500 Points", "key":"le"},
    {"name":"Silver 4", "value":"450 Points", "key":"s4"},
    {"name":"Gold Nova Master", "value":"1750 Points", "key":"gnm"},
    {"name":"Legendary Eagle Master", "value":"10000 Points", "key":"lem"},
    {"name":"Silver Elite", "value":"600 Points", "key":"se"},
    {"name":"Master Guardian 1", "value":"2450 Points", "key":"mg1"},
    {"name":"Supreme Master First Class", "value":"15000 Points", "key":"smfc"},
    {"name":"Silver Elite Master", "value":"850 Points", "key":"sem"},
    {"name":"Master Guardian 2", "value":"2750 Points", "key":"mg2"},
    {"name":"The Global Elite", "value":"18000 Points", "key":"ge"}
]

class csfire(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def evidence(self, ctx):
        """
        !evidence implemented as [p]evidence
        """
        embed=Embed(title="**THIS CHANNEL IS FOR EVIDENCE ONLY**", description="- Post the EVIDENCE\n - Post their steam profile link\n  - Mention what server they are on\n - And let us know what they are doing (cheating, trolling, griefing, etc)", color=0xe06100)
        embed.add_field(name="To report a player in-game", value="- Type !calladmin in-game\n - Select a player you would like to report\n - Type the reason for this report then press enter", inline=False)
        await ctx.message.channel.send(embed=embed)
        await ctx.message.delete()

    @commands.command(pass_context=True)
    async def rules(self, ctx):
        """
        !rules implemented as [p]rules. Takes [Rule Number] as an argument.
        """
        embed = Embed(title="**RULES**", color=FA8500)

        # Check if a specific rule was been chosen
        args = ctx.message.content.split(" ")
        rule_n = 0

        for arg in args:
            if arg.isnumeric() and len(arg) == 1:
                rule_n = int(arg)
                break
            else:
                continue

        if rule_n in range(1, 9):
            embed.add_field(name=CSFIRE_RULES[rule_n - 1]["name"], value=CSFIRE_RULES[rule_n - 1]["value"], inline=False)
            embed.title = "**RULE {}**".format(str(rule_n))
        else:
            for rule in CSFIRE_RULES:
                embed.add_field(name=rule["name"], value=rule["value"], inline=False)

        await ctx.message.channel.send(embed=embed)
        await ctx.message.delete()
    
    @commands.command(pass_context=True)
    async def rank(self, ctx):
        """
        !rank implemented as [p]rank. Takes argument [rank key]/[rank name] to get one rank returned.
        """
        embed = Embed(title="**Ranks**", color=FA8500)
        
        # Check if a specific rank was been chosen
        args = ctx.message.content.split(" ")
        rank_x = False

        for arg in args:
            if arg in [x["key"] for x in CSFIRE_RANKS]:
                rank_x = True
                rank = [rank for rank in CSFIRE_RANKS if rank["key"] == arg][0]
                embed.add_field(name=rank["name"], value=rank["value"], inline=True)
        
        if len(args) >= 2 and not rank_x:
            arg = " ".join(args[1:]).lower()

            if arg in [name["name"].lower() for name in CSFIRE_RANKS]:
                rank_x = True
                rank = [rank for rank in CSFIRE_RANKS if rank["name"].lower() == arg][0]
                embed.add_field(name=rank["name"], value=rank["value"], inline=True)

        if not rank_x:
            for rank in CSFIRE_RANKS:
                embed.add_field(name=rank["name"], value=rank["value"], inline=True)

        await ctx.message.channel.send(embed=embed)
        await ctx.message.delete()

    @commands.command(pass_context=True)
    async def activity(self, ctx):
        """
        !activity implemnted as [p]activity
        """
        embed=Embed(title="**https://csfire.xyz/stats/**", url="https://csfire.xyz/stats/", color=FA8500)
        embed.set_author(name="See your activity on")
        await ctx.message.channel.send(embed=embed)
        await ctx.message.delete()

    @commands.command(pass_context=True)
    async def appeal(self, ctx):
        """
        !appeal implemented as [p]appeal
        """
        embed=Embed(title="**How to appeal your ban?**", description="- Post your steam profile link\n- Wait for an admin to reply\n- Do NOT tag admins or owners", color=FA8500)
        await ctx.message.channel.send(embed=embed)
        await ctx.message.delete()

    @commands.command(pass_context=True)
    async def group(self, ctx):
        """
        !group implemented as [p]group
        """
        embed = Embed(title="Steam Community :: Group :: CSFIRE Community", url="https://steamcommunity.com/groups/csfirecommunity", description="", color=0xfdfaff)
        embed.set_thumbnail(url="https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/b0/x.jpg")
        await ctx.message.channel.send("https://steamcommunity.com/groups/csfirecommunity", embed=embed)
    
    @commands.command(pass_context=True)
    async def connect(self, ctx):
        """
        !servers implemented as [p]connect. Takes 2 arguments [server number] and [server region] the latter is optional.
        """
        embed = Embed(title="No server selected showing connection info", color=FA8500)

        args = ctx.message.content.split(" ")[1:]

        valid_numbers_ch = range(1, len(CSFIRE_SERVERS["ch"]) + 1)
        valid_numbers_al = range(1, len(CSFIRE_SERVERS["al"]) + 1)
        server_number = 0
        server_region = "ch" if "ch" in args else "al"

        for arg in args:
            if arg.isnumeric():
                if int(arg) in (valid_numbers_al if server_region == "al" else valid_numbers_ch):
                    server_number = int(arg)

            elif arg in ["%", "?"] or "ran" in arg:
                server_number = choice(valid_numbers_na)

        if not server_number:
            for i, al_ip in enumerate(CSFIRE_SERVERS["al"]):
                embed.add_field(name=CSFIRE_SERVERS["meta"]["al"].format(str(i+1)), value=al_ip, inline=True)
            
            for i, ch_ip in enumerate(CSFIRE_SERVERS["ch"]):
                embed.add_field(name=CSFIRE_SERVERS["meta"]["ch"].format(str(i+1)), value=ch_ip, inline=True)
        
        else:
            server_ip = CSFIRE_SERVERS[server_region][server_number - 1]
            server_name = CSFIRE_SERVERS["meta"][server_region].format(str(server_number))
            ip_con = CSFIRE_SERVERS["meta"]["ip"].format(server_ip)
            embed.title = "{}\n({})".format(server_name, ip_con)
        
        await ctx.message.channel.send(embed=embed)
        await ctx.message.delete()
    
    @commands.command(pass_context=True)
    async def unprivate(self, ctx):
        """
        Command on insolence requests sharing a gif on how to unprivate. [p]unprivate
        """
        embed = Embed(title="Unprivating game details", color=FA8500)
        embed.set_image(url="https://s.put.re/ZYs3eYf4.gif")
        await ctx.message.channel.send(embed=embed)
        await ctx.message.delete()

    @commands.command(pass_context=True)
    async def google(self, ctx):
        """
        [p]google <search_terms> Let's you search with google.
        """
        args = ctx.message.content.split(" ")[1:]
        
        if len(args) > 0:
            search_query = '+'.join(args)
            google_search = "https://google.com/search?q=" + search_query
            await ctx.message.channel.send(google_search)
        else:
            await ctx.message.channel.send("""```-google <search_terms>
Creates a google link```
            """)

    @commands.command(pass_context=True)
    async def spam(self, ctx):
        """
        [p]spam @user [amount of messages]
        """        
        SPAM_DURATiON = 1
        if (ctx.message.author.permissions_in(ctx.message.channel).kick_members):
            args = ctx.message.content.split(" ")[1:]
            await ctx.message.delete()

            if len(ctx.message.mentions) == 1:
                spam_string = "<@{}> ".format(ctx.message.mentions[0].id)
                
                
                if len(args) == 2 and args[1].isnumeric():
                    SPAM_DURATiON = int(args[1])
                
                while True:
                    if len(spam_string) < 2000 - len(spam_string):
                        spam_string += spam_string + spam_string
                    else:
                        break
                    
                for i in range(0, SPAM_DURATiON):
                    await ctx.message.channel.send(spam_string, delete_after=0.0)
            
            else:
                await ctx.message.channel.send("No user mentioned")

    @commands.command(pass_context=True)
    async def recover(self, ctx):
        await ctx.message.channel.send(CSFIRE_RECOVER_URL)
        await ctx.message.delete()
        
        
    @commands.command(pass_context=True)
    async def copyurl(self, ctx):
        """
        Command on Insolence's request sharing a gif on how to copy Steam URL. [p]copyurl
        """
        embed = Embed(title="Copying your Steam Profile Link", color=FA8500)
        embed.set_image(url="https://i.imgur.com/M3LDnJm.gif")
        await ctx.message.channel.send(embed=embed)
        await ctx.message.delete()
