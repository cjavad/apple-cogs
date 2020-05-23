from .steam import steam

def setup(bot):
    bot.add_cog(steam(bot))