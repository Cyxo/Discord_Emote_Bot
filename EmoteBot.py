#! /usr/bin/python3
import discord
from discord.ext import commands
from token_value import token
import discord.utils
import subprocess
import requests
import re


class EmoteBot():
    def __init__(self):
        self.bot = commands.Bot(command_prefix = '<')
        self.enable = False
        self.commands = ['<commands', '<ping', '<storage', '<show_list', '<emote', '<add',
                         '<remove', '<rename']
        self.commands_usage = ['<commands: show this list.',
                               '<ping: return Pong!',
                               '<storage: print actual storage',
                               '<show_list: show emotes',
                               '<emote name_emote: post name_emote',
                               '<add link emote_name: add a New emote',
                               '<remove: remove an emote',
                               '<rename name_old_emote name_new_emote: rename an emote'
                              ]
        self.suported_types = ["PNG", "GIF", "JPEG"]
        self.max_storage = 1000000


    # console colors
    def red(self, msg): print('\033[91m[!] {}\033[00m' .format(msg))
    def green(self, msg): print('\033[92m[+] {}\033[00m' .format(msg))
    def yellow(self, msg): print('\033[93m[+] {}\033[00m' .format(msg))
    def blue(self, msg): print('\033[94m[*] {}\033[00m' .format(msg))
    def purple(self, msg): print('\033[95m[*] {}\033[00m' .format(msg))
    def cyan(self, msg): print('\033[96m[*] {}\033[00m' .format(msg))

    def show_attributes_from(self, object):
        self.cyan('\n'.join(i for i in dir(object) if not i.startswith('__')))

    async def process(self, cmd):
        p = subprocess.Popen(cmd,
                             shell=True,
                             bufsize=64,
                             stdin=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             stdout=subprocess.PIPE)
        return [ item.decode() for item in p.communicate()[0].split(b'\n')[:-1] ]

    def catch(self):

        @self.bot.event
        async def on_ready():
            self.green('EmoteBot is coming !')
            
        @self.bot.command() 
        async def commands():
            await self.bot.say("```{}```".format('\n'.join(self.commands_usage)))

        @self.bot.command() 
        async def ping():
            await self.bot.say("```Pong!```")

        @self.bot.command() 
        async def show_list():
            files = await self.process("ls emotes")
            for i in range(len(files)):
                files[i] = files[i][:-4]
            await self.bot.say("```Emotes :\n{}```".format('\n'.join(files)))

        @self.bot.command(pass_context = True)
        async def emote(ctx):
            words = ctx.message.content.split(' ')
            await self.bot.delete_message(ctx.message)
            if len(words)!=2:
                await self.bot.say("```Command <emote takes 1 args : <emote emote_name```")
                return
            test = await self.process("ls emotes")
            if not words[1]+'.gif' in test:
                await self.bot.say("```Emote {} not found```".format(words[1]))
                return
            await self.bot.send_file(ctx.message.channel, "emotes/{}.gif".format(words[1]),filename="{}.gif".format(words[1]),content="{} :".format(ctx.message.author.mention))


        @self.bot.command(pass_context = True)
        async def add(ctx):
            pattern = "^[A-Za-z0-9_-]*$"
            words = ctx.message.content.split(' ')
            if len(words) != 3:
                await self.bot.say("```Command <add takes 2 args : <add link emote_name```")
                return
            test = await self.process("ls emotes")
            if words[2]+'.gif' in test:
                await self.bot.say("```This name is already on an emote```")
                return
            if not re.match(pattern, words[2]):
                await self.bot.say("```The name of your emote must comtain only alphanumeric characters, minus and underscores```")
                return
            storage = await self.process("du -s emotes | cut -f1")
            if int(storage[0]) > self.max_storage:
                await self.bot.say("```There in no place anymore, please remove emotes```")
                return
            try:
                link = words[1]
                r = requests.get(link)
                if r.status_code != 200:
                    await self.bot.say("```The link doesn't respond ;(```")
                    return
                filename = "emotes/{}.gif".format(words[2])
                with open(filename, 'wb') as f:
                    f.write(r.content)
                ftype = await self.process('file emotes/{}.gif | cut -d" " -f2'.format(words[2]))
                if not ftype[0] in self.suported_types:
                    await self.bot.say("```Your file type is : {}, please use {} files```".format(ftype[0], " ".join(self.suported_types)))
                    await self.process("rm -f emotes/{}.gif".format(words[2]))
                    return
                await self.bot.delete_message(ctx.message)
                await self.bot.say("```New emote : {} added!```".format(words[2]))
            except Exception as exception:
                await self.bot.say("```The link doesn't work ;(```")

        @self.bot.command(pass_context = True)
        async def remove(ctx):
            words = ctx.message.content.split(' ')
            if len(words)!=2:
                await self.bot.say("```Command <remove takes 1 args : <remove emote_name```")
                return
            test = await self.process("ls emotes")
            if not words[1]+'.gif' in test:
                await self.bot.say("```Emote not found``")
                return
            await self.process("rm -f emotes/{}.gif".format(words[1]))
            await self.bot.say("```Emote : {} removed```".format(words[1]))
            
        @self.bot.command(pass_context = True)
        async def rename(ctx):
            pattern = "^[A-Za-z0-9_-]*$"
            words = ctx.message.content.split(' ')
            if len(words)!=3:
                await self.bot.say("```Command <rename takes 2 args : <remove old_emote_name new_emote_name```")
                return
            test = await self.process("ls emotes")
            if not words[1]+'.gif' in test:
                await self.bot.say("```Emote not found```")
                return
            if not re.match(pattern, words[2]):
                await self.bot.say("```The name of your emote must comtain only alphanumeric characters, minus and underscores```")
                return
            await self.process("mv emotes/{}.gif emotes/{}.gif".format(words[1], words[2]))
            await self.bot.say("```Emote : {} successfully renamed in {}```".format(words[1], words[2]))

        @self.bot.command()
        async def storage():
            storage = await self.process("du -s emotes | cut -f1")
            await self.bot.say("```There is a storage of {}Mo / {}Mo```".format(int(storage[0])//1000, self.max_storage//1000))



    def start(self):
        self.catch()
        self.bot.run(token)

if __name__ == "__main__":
    bot = EmoteBot()
    bot.start()
