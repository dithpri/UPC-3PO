import discord

from discord.ui import View

class IdView(View):
    def __init__(self, ctx, id_pages):
        super().__init__()
        self.ctx = ctx
        self.id_pages = id_pages
        self.current = 0


    @discord.ui.button(label="🡰", style=discord.ButtonStyle.blurple, disabled=True)
    async def back_callback(self, interaction: discord.Interaction, button):
        if interaction.user != self.ctx.message.author:
            return

        self.children[1].disabled = False
        self.current -= 1

        if self.current == 0:
            self.children[0].disabled = True

        await interaction.response.edit_message(embed=self.id_pages[self.current], view=self)


    @discord.ui.button(label="🡲", style=discord.ButtonStyle.blurple)
    async def forward_callback(self, interaction: discord.Interaction, button):
        if interaction.user != self.ctx.message.author:
            return

        self.children[0].disabled = False
        self.current += 1

        if self.current == len(self.id_pages) - 1:
            self.children[1].disabled = True

        await interaction.response.edit_message(embed=self.id_pages[self.current], view=self)


    @discord.ui.button(label="✖", style=discord.ButtonStyle.danger)
    async def cancel_callback(self, interaction: discord.Interaction, button):
        if interaction.user != self.ctx.message.author:
            return

        self.value = None
        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(view=self)
        self.stop()


    async def on_timeout(self):
        self.value = None
        for child in self.children:
            child.disabled = True

        await self.message.edit(view=self)
        self.stop()