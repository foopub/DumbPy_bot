from discord.ext import commands, tasks
import discord
from typing import Optional, Union
import time
import datetime as dt
import dateparser as dtp
#import schedule as sch
import sched
import heapq


class asched(sched.scheduler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def arun(self):
        lock = self._lock
        q = self._queue
        delayfunc = self.delayfunc
        timefunc = self.timefunc
        pop = heapq.heappop
        while True:
            with lock:
                if not q:
                    break
                time, priority, action, argument, kwargs = q[0]
                now = timefunc()
                if time > now:
                    delay = True
                else:
                    delay = False
                    pop(q)
            if delay:
                return time - now
            else:
                await action(*argument, **kwargs)
                delayfunc(0)


class Scheduler(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        #self.mainloop.start()
        self.schedule = asched(time.time,time.sleep)
        self.count = 0

    @tasks.loop(seconds=5)
    async def mainloop(self):
        print(self.count)
        self.count += 1
        await self.schedule.arun()
    
    @commands.command(name='remind')
    async def remind(self, context: commands.Context,
            channel: Optional[discord.TextChannel],
            member: Optional[discord.Member],
            message: str,
            *, dtime: str):
        """
        Schedule a reminder, message must be enclosed in "".
        This function uses the dateparser python module to convert natural
        language times to a valid datetime.

        """
        if not channel:
            channel = context.channel
        if not member:
            member =  context.author

        absdtime = dtp.parse(dtime).timestamp()
        
        self.schedule.enterabs(
                absdtime,1,channel.send,(message + member.mention,))


    @commands.group(name='event', alias='events')
    async def event(self, context: commands.Context):
        """
        Schedule a command to be executed at a given time.
        """
        pass

    @event.command(name='stop')
    async def stop(self, context: commands.Context):
        self.mainloop.stop()

    @event.command(name='start')
    async def start(self, context: commands.Context):
        self.mainloop.start()

    @event.command(name='add')
    async def add(self, context: commands.Context):
        pass
 
    @event.command(name='edit')
    async def edit(self, context: commands.Context):
        pass

    @event.command(name='list')
    async def list(self, context: commands.Context):
        await context.send('```' + str(self.schedule.queue) + '```')
        pass

    @event.command(name='remove')
    async def remove(self, context: commands.Context):
        pass

def setup(client: commands.Bot) -> None:
    client.add_cog(Scheduler(client))
    
