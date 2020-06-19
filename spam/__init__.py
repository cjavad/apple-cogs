from .spam import spam

def setup(bot):
    bot.add_cog(spam(bot))
