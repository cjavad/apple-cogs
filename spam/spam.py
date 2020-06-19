from redbot.core import commands

class spam(commands.Cogs):
    def __init__(self, bot):
        self.bot = bot
       
    @commands.command(pass_context=True)
    async def spam(self, ctx):
        """
        [p]spam @user [amount of messages]
        """        
        SPAM_DURATION = 1
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
                    
                for i in range(0, SPAM_DURATION):
                    await ctx.message.channel.send(spam_string, delete_after=0.0)
            
            else:
                await ctx.message.channel.send("No user mentioned")
