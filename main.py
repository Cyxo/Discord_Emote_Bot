#! /usr/bin/python3

import os

import discord
import discord.utils
import requests
import re

from discord.ext import commands
from token_value import token

from config import (config_prefix, config_suported_types, config_pattern,
                    config_max_storage, config_max_name_length,
                    config_message_by_line, config_max_message_length,
                    config_max_emote_length, config_pong)


class EmoteBot():
    def __init__(self):
        self.prefix = config_prefix
        self.bot = commands.Bot(command_prefix=self.prefix)
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
        async def on_command_error(ctx, exc):
            # Detect mentions
            if re.match(r"<@!?\d{18}>", ctx.message.content):
                return
            try:
                await ctx.message.delete()
            except discord.Forbidden:
                None

            command = ctx.message.content[1:].split(" ")[0]
            if command in self.bot.all_commands:
                ctx.message.content = self.prefix + "help " + command
                await self.bot.process_commands(ctx.message)
                return
            test = os.listdir("emotes")
            if command + ".gif" in test:
                await ctx.send(file=discord.File("emotes/{}.gif".format(command)),
                             content="{} reacted with {} :"
                             .format(ctx.message.author.mention, command))
                return

            # Display an error message if the command is not found, because
            # we still delete their message
            await ctx.send(f'```Command or emote "{command}" not found```')

        @self.bot.command()
        async def ping(ctx):
            """ Ping da bot """
            await ctx.send("```{}```".format(self.pong))

        @self.bot.command(aliases = ['list'])
        async def show_list(ctx):
            """ Show the list of emotes """
            files = sorted(os.listdir("emotes"))
            odd = 1
            message = ""
            for i in range(len(files)):
                files[i] = files[i][:-4]
                if odd % self.message_by_line == 0:
                    files[i] += "\n"
                else:
                    files[i] += " " * (self.max_name_length + 2 -
                                       len(files[i]))
                message += files[i]
                odd += 1
                message_length = len(message) + (self.max_name_length) + 2 + 6
                if message_length > self.max_message_length:
                    await ctx.send("```{}```".format(message))
                    message = ""
                    odd = 0
            if message != "":
                await ctx.send("```\n{}```".format(message))

        @self.bot.command()
        async def emote(ctx, name):
            """ Send the gif which you specify """
            try:
                await ctx.message.delete()
            except discord.Forbidden:
                None
            name = name.lower()
            test = os.listdir("emotes")
            if not name + ".gif" in test:
                await ctx.send("```Emote {} not found```".format(name))
                return
            await ctx.send(file=discord.File("emotes/{}.gif".format(name)),
                           content="{} reacted with {} :"
                           .format(ctx.message.author.mention, name))

        @self.bot.command()
        async def add(ctx, link, name):
            """ Add an emote to the database """
            try:
                await ctx.message.delete()
            except discord.Forbidden:
                None
            name = name.lower()
            test = os.listdir("emotes")
            if name+".gif" in test:
                await ctx.send("```This name is already on an emote```")
                return
            if not re.match(self.pattern, name):
                await ctx.send("```The name of your emote must contain "
                               "only alphanumeric characters and "
                               "underscores```")
                return
            if len(name) > self.max_name_length:
                await ctx.send("```The name of your emote is too long, "
                               "it must contain less than {} characters```"
                               "".format(self.max_name_length))
                return
            storage = 0
            for files in os.scandir("emotes"):
                if not (files.name.startswith(".")):
                    storage += os.path.getsize("emotes/{}".format(files.name))
            if storage > self.max_storage:
                await ctx.send("```There in no place anymore, please "
                               "remove emotes```")
                return
            try:
                r = requests.head(link)
            except requests.exceptions.MissingSchema:
                await ctx.send("```The link doesn't work ;(```")
                return
            if r.status_code != 200:
                await ctx.send("```The link doesn't respond ;(```")
                return
            if not ("image" in r.headers["Content-Type"]):
                await ctx.send("```Your content type is {}, please use "
                               "images```"
                               "".format(r.headers["Content-Type"]))
                return
            if int(r.headers["Content-Length"]) > self.max_emote_length:
                await ctx.send("```Your file is too heavy, "
                               "max weight is : {}Mo```"
                               "".format(self.
                                         max_emote_length//(int(1E6))))
                return
            filename = "emotes/{}.gif".format(name)
            with open(filename, "wb") as f:
                f.write(requests.get(link).content)
            await ctx.send("```New emote : {} added!```".format(name))

        @self.bot.command()
        async def remove(ctx, name):
            """ Remove an emote of the database """
            name = name.lower()
            test = os.listdir("emotes")
            if name+".gif" not in test:
                await ctx.send("```Emote not found```")
                return
            os.remove("emotes/{}.gif".format(name))
            await ctx.send("```Emote : {} removed```".format(name))

        @self.bot.command()
        async def rename(ctx, old, new):
            """ Rename an emote """
            old = old.lower()
            new = new.lower()
            test = os.listdir("emotes")
            if old + ".gif" not in test:
                await ctx.send("```Emote not found```")
                return
            if new + ".gif" in test:
                await ctx.send("```Emote already exist```")
                return
            if not re.match(self.pattern, new):
                await ctx.send("```The name of your emote must comtain "
                               "only alphanumeric characters and "
                               "underscores```")
                return
            if len(new) > self.max_name_length:
                await ctx.send("```The name of your emote is too long, "
                               "it must contain less than {} characters```"
                               "".format(self.max_name_length))
                return
            os.rename("emotes/{}.gif".format(old), "emotes/{}.gif".format(new))
            await ctx.send("```Emote : {} successfully renamed in {}```"
                           "".format(old, new))

        @self.bot.command()
        async def storage(ctx):
            """ Display the remaining storage """
            storage = 0
            for files in os.scandir("emotes"):
                if not (files.name.startswith(".")):
                    storage += os.path.getsize("emotes/{}".format(files.name))
            await ctx.send("```There is a storage of {}Mo / {}Mo```"
                           "".format(storage//int(1E6),
                                     self.max_storage//(int(1E6))))

    def start(self):
        self.catch()
        self.bot.run(token)


if __name__ == "__main__":
    bot = EmoteBot()
    bot.start()
