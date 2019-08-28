#! /usr/bin/python3

import os

import discord
import discord.utils
import requests
import re
import shutil

from discord.ext import commands
from token_value import token

from config import (config_prefix, config_suported_types, config_pattern, 
                    config_max_storage, config_max_name_length, 
                    config_message_by_line, config_max_message_length, 
                    config_max_emote_length, config_pong)


class EmoteBot():
    def __init__(self):
        self.prefix = config_prefix
        self.bot = commands.Bot(command_prefix = self.prefix)
        self.suported_types = config_suported_types
        self.pattern = config_pattern
        self.max_storage = config_max_storage
        self.max_name_length = config_max_name_length
        self.message_by_line = config_message_by_line
        self.max_message_length = config_max_message_length
        self.max_emote_length = config_max_emote_length
        self.pong = config_pong

    def green(self, msg): print("\033[92m[+] {}\033[00m".format(msg))

    def catch(self):

        @self.bot.event
        async def on_ready():
            self.green("EmoteBot is coming !")

        @self.bot.event                                                                  
        async def on_command_error(exc, ctx):                                           
            command = ctx.message.content[1:].split(" ")[0]
            if not command in self.bot.commands:
                return
            ctx.message.content = self.prefix + "help " + command
            await self.bot.process_commands(ctx.message)                                  
            
        @self.bot.command() 
        async def ping():
            """ Ping da bot """
            await self.bot.say("```{}```".format(self.pong))

        @self.bot.command() 
        async def show_list():
            """ Show the list of emotes """
            files = os.listdir("emotes")
            files.sort()
            odd = 0
            message = ""
            for i in range(len(files)):
                files[i] = files[i][:-4]
                if odd%self.message_by_line == 0:
                    files[i] += "\n"
                else:
                    files[i] += " " * (self.max_name_length + 2 -
                                       len(files[i]))
                message += files[i]
                odd += 1
                message_length = len(message) + (self.max_name_length) + 2 + 6
                if message_length > self.max_message_length:
                    await self.bot.say("```{}```".format(message))
                    message = ""
                    odd = 0
            if message != "":
                await self.bot.say("```{}```".format(message))

        @self.bot.command(pass_context = True)
        async def emote(ctx, name):
            """ Send the gif which you specify """
            try:
                await self.bot.delete_message(ctx.message)
            except discord.Forbidden:
                None
            name = name.lower()
            test = os.listdir("emotes")
            if not name +".gif" in test:
                await self.bot.say("```Emote {} not found```".format(name))
                return
            await self.bot.send_file(ctx.message.channel, 
                                     "emotes/{}.gif".format(name),
                                     filename="{}.gif".format(name),
                                     content="{} reacted with {} :"
                                     .format(ctx.message.author.mention, name))


        @self.bot.command(pass_context = True)
        async def add(ctx, link, name):
            """ Add an emote to the database """
            try:
                await self.bot.delete_message(ctx.message)
            except discord.Forbidden:
                None
            name = name.lower()
            test = os.listdir("emotes")
            if name+".gif" in test:
                await self.bot.say("```This name is already on an emote```")
                return
            if not re.match(self.pattern, name):
                await self.bot.say("```The name of your emote must contain "
                                   "only alphanumeric characters and "
                                   "underscores```")
                return
            if len(name) > self.max_name_length:
                await self.bot.say("```The name of your emote is too long, "
                                   "it must contain less than {} characters```"
                                   "".format(self.max_name_length))
                return
            storage = 0
            for files in os.scandir("emotes"):
                if not ( files.name.startswith(".") ):
                    storage += os.path.getsize("emotes/{}".format(files.name))
            if storage > self.max_storage:
                await self.bot.say("```There in no place anymore, please "
                                   "remove emotes```")
                return
            try:
                r = requests.head(link)
            except requests.exceptions.MissingSchema:
                await self.bot.say("```The link doesn't work ;(```")
                return
            if r.status_code != 200:
                await self.bot.say("```The link doesn't respond ;(```")
                return
            if not ( "image" in r.headers["Content-Type"] ):
                await self.bot.say("```Your content type is {}, please use "
                                   "images```"
                                   "".format(r.headers["Content-Type"]))
                return
            if int(r.headers["Content-Length"]) > self.max_emote_length:
                await self.bot.say("```Your file is too heavy, "
                                   "max weight is : {}Mo```"
                                   "".format(self.max_emote_length//(int(1E6))))
                return
            filename = "emotes/{}.gif".format(name)
            with open(filename, "wb") as f:
                f.write(requests.get(link).content)
            await self.bot.say("```New emote : {} added!```".format(name))

        @self.bot.command(pass_context = True)
        async def remove(ctx, name):
            """ Remove an emote of the database """
            name = name.lower()
            test = os.listdir("emotes")
            if not name+".gif" in test:
                await self.bot.say("```Emote not found```")
                return
            os.remove("emotes/{}.gif".format(name))
            await self.bot.say("```Emote : {} removed```".format(name))
            
        @self.bot.command(pass_context = True)
        async def rename(ctx, old, new):
            """ Rename an emote """
            old = name.lower()
            new = new.lower()
            test = os.listdir("emotes")
            if not old+".gif" in test:
                await self.bot.say("```Emote not found```")
                return
            if not re.match(self.pattern, new):
                await self.bot.say("```The name of your emote must comtain "
                                   "only alphanumeric characters and "
                                   "underscores```")
                return
            if len(new) > self.max_name_length:
                await self.bot.say("```The name of your emote is too long, "
                                   "it must contain less than {} characters```"
                                   "".format(self.max_name_length))
                return
            os.rename("emotes/{}.gif".format(old), "emotes/{}.gif".format(new))
            await self.bot.say("```Emote : {} successfully renamed in {}```"
                               "".format(old, new))

        @self.bot.command()
        async def storage():
            """ Display the remaining storage """
            storage = 0
            for files in os.scandir("emotes"):
                if not ( files.name.startswith(".") ):
                    storage += os.path.getsize("emotes/{}".format(files.name))
            await self.bot.say("```There is a storage of {}Mo / {}Mo```"
                               "".format(storage//int(1E6), 
                                       self.max_storage//(int(1E6))))

    def start(self):
        self.catch()
        self.bot.run(token)

if __name__ == "__main__":
    bot = EmoteBot()
    bot.start()
