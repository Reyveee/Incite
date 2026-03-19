import discord
import numpy as np
import random
import string
import Augmentor
import os
import shutil
import asyncio
import time
from discord.ext import commands
from discord.utils import get
from PIL import Image, ImageDraw, ImageFont
from utils.Tools import *
from utils.logMessage import sendLogMessage 
from discord.ui import Button, View, Modal, TextInput

# ------------------------ COGS ------------------------ #  

class OnJoinCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

# ------------------------------------------------------ #  

    @commands.Cog.listener()
    async def on_member_join(self, member):

        if (member.bot):
            return

        # Read configuration.json
        data = getConfig(member.guild.id)
        logChannel = data["logChannel"]
        captchaChannel = self.bot.get_channel(data["captchaChannel"])

        memberTime = f"{member.joined_at.year}-{member.joined_at.month}-{member.joined_at.day} {member.joined_at.hour}:{member.joined_at.minute}:{member.joined_at.second}"

        if data["captcha"] is True:
            
            try:
                getrole = get(member.guild.roles, id=data["temporaryRole"])
                if getrole is not None:
                    await member.add_roles(getrole)
            except Exception as e:
                print(f"An error occurred while adding role to member: {e}")

            image = np.zeros(shape= (100, 350, 3), dtype= np.uint8)

            image = Image.fromarray(image+255)

            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype(font="utils/arial.ttf", size=60)

            text = ' '.join(random.choice(string.ascii_uppercase) for _ in range(6))
            password = text.replace(" ", "") 

            W, H = (350, 100)
            bbox = draw.textbbox((0, 0), text, font=font)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text(((W - w) / 2, (H - h) / 2), text, font=font, fill=(90, 90, 90))

            ID = member.id
            folderPath = f"captchaFolder/{member.guild.id}/captcha_{ID}"
            try:
                os.mkdir(folderPath)
            except:
                if os.path.isdir(f"captchaFolder/{member.guild.id}") is False:
                    os.mkdir(f"captchaFolder/{member.guild.id}")
                if os.path.isdir(folderPath) is True:
                    shutil.rmtree(folderPath)
                os.mkdir(folderPath)
            image.save(f"{folderPath}/captcha{ID}.png")

            p = Augmentor.Pipeline(folderPath)
            p.random_distortion(probability=1, grid_width=4, grid_height=4, magnitude=14)
            p.process()

            path = f"{folderPath}/output"
            files = os.listdir(path)
            captchaName = [i for i in files if i.endswith('.png')]
            captchaName = captchaName[0]

            image = Image.open(f"{folderPath}/output/{captchaName}")
            
            width = random.randrange(6, 8)
            co1 = random.randrange(0, 75)
            co3 = random.randrange(275, 350)
            co2 = random.randrange(40, 65)
            co4 = random.randrange(40, 65)
            draw = ImageDraw.Draw(image)
            draw.line([(co1, co2), (co3, co4)], width= width, fill= (90, 90, 90))
            
            noisePercentage = 0.25 

            pixels = image.load() 
            for i in range(image.size[0]):
                for j in range(image.size[1]):
                    rdn = random.random()
                    if rdn < noisePercentage:
                        pixels[i,j] = (90, 90, 90)

            image.save(f"{folderPath}/output/{captchaName}_2.png")

            captchaFile = discord.File(f"{folderPath}/output/{captchaName}_2.png")
            embed = discord.Embed(title="You must pass the captcha verification to access the server!", description="Enter the captcha to access to the whole server (only 6 uppercase letters).", color=0x000000)
            embed.set_image(url=f"attachment://{captchaFile.filename}")
            embed.set_author(name=member.display_name, icon_url=member.display_avatar)
            submit_button = Button(label="Submit Answer", style=discord.ButtonStyle.primary)

            class CaptchaModal(Modal):
                def __init__(self, bot, password):
                    super().__init__(title="Captcha Verification")
                    self.bot = bot
                    self.password = password
                    self.answer = TextInput(label="Enter Captcha", placeholder="Enter the captcha here", required=True)
                    self.add_item(self.answer)

                async def on_submit(self, interaction: discord.Interaction):
                    if self.answer.value == self.password:
                        await interaction.response.send_message(f"Correct! Welcome {member.mention}.", ephemeral=True)
                        try:
                            getrole = get(member.guild.roles, id=data["roleGivenAfterCaptcha"])
                            if getrole is not None:
                                await member.add_roles(getrole)
                            else:
                                raise ValueError("Role to be given after captcha does not exist.")
                        except discord.errors.Forbidden:
                            embed = discord.Embed(description="Missing permissions to add roles.", color=0x000000)
                            embed.timestamp = discord.utils.utcnow()
                           # await sendLogMessage(self.bot, event=member, channel=logChannel, embed=embed)
                        except Exception as error:
                            embed = discord.Embed(description=f"Give and remove roles failed: {error}", color=0x000000)
                            embed.timestamp = discord.utils.utcnow()
                            #await sendLogMessage(self.bot, event=member, channel=logChannel, embed=embed)
                        try:
                            getrole = get(member.guild.roles, id=data["temporaryRole"])
                            if getrole is not None:  # Check if role exists
                                await member.remove_roles(getrole)
                            else:
                                raise ValueError("Temporary role does not exist.")
                        except Exception as error:
                            embed = discord.Embed(description=f"No temp role found: {error}", color=0x000000)
                            embed.timestamp = discord.utils.utcnow()
                            #await sendLogMessage(self.bot, event=member, channel=logChannel, embed=embed)
                        time.sleep(3)
                        try:
                            await captchaEmbed.delete()
                        except discord.errors.NotFound:
                            pass
                        #Log
                        embed = discord.Embed(title=f"{member.name} passed the captcha verification.", description=f"__User information:__\n\n**Name:** {member}\n**Id:** {member.id}", color=0x361836)
                        embed.set_footer(text=f"{memberTime}")
                        await sendLogMessage(self.bot, event=member, channel=logChannel, embed=embed)

                    else:
                        await interaction.response.send_message("Incorrect captcha. Please try again.", ephemeral=True)

            async def submit_callback(interaction):
                if interaction.user == member:
                    await interaction.response.send_modal(CaptchaModal(self.bot, password))

            submit_button.callback = submit_callback

            view = View()
            view.add_item(submit_button)

            captchaEmbed = await captchaChannel.send(content=f"{member.mention}", embed=embed, file=captchaFile, view=view)
            try:
                shutil.rmtree(folderPath)
            except Exception as error:
                print(f"Delete captcha file failed {error}")


