import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import os

# --- Keep-alive web server for Render ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run).start()

# --- Config ---
TOKEN = os.environ.get("TOKEN")
VERIFIED_ROLE_NAME = "Verified"  # Must already exist in your server

# --- Setup ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


# --- The verify button ---
class VerifyButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="✅ Verify",
        style=discord.ButtonStyle.success,
        custom_id="verify_button",
    )
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, name=VERIFIED_ROLE_NAME)

        if role is None:
            await interaction.response.send_message(
                f"❌ Role `{VERIFIED_ROLE_NAME}` not found. Ask an admin to create it.",
                ephemeral=True,
            )
            return

        if role in interaction.user.roles:
            await interaction.response.send_message(
                "You're already verified! ✅",
                ephemeral=True,
            )
            return

        await interaction.user.add_roles(role)
        await interaction.response.send_message(
            f"✅ You've been verified and given the `{VERIFIED_ROLE_NAME}` role!",
            ephemeral=True,
        )


# --- Register persistent view on startup ---
@bot.event
async def on_ready():
    bot.add_view(VerifyButton())
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")


# --- !setup command (admin only) ---
@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    """Posts the verification message with the button."""
    await ctx.message.delete()
    embed = discord.Embed(
        title="✅ Verification",
        description="Click the button below to verify yourself and gain access to the server.",
        color=discord.Color.green(),
    )
    await ctx.send(embed=embed, view=VerifyButton())


# --- Error handling ---
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need Administrator permission to use this command.", delete_after=5)
    else:
        raise error


bot.run(TOKEN)