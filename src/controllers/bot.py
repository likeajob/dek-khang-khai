from decimal import Decimal
from discord.ext.commands import AutoShardedBot
from src.commands.dataservice import DataService
from src.commands.general import General
from src.commands.text2speech import Text2Speech
from src.controllers.autoTasks import AutoTasks
from src.events.general import General as GE
from src.utils.configs.app_settings import get_settings
from src.utils.helpers.logging import setup_logging
import discord
import logging

intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.members = True
intents.message_content = True

class Bot(AutoShardedBot):
    def __init__(self) -> None:
        super().__init__(command_prefix=get_settings().PREFIX, intents=intents)
        self.ge = GE()
        self.t2p = Text2Speech()
        self.ds = DataService()
        self.general = General()
        self.at = AutoTasks(self)
        self.add_commands()

    async def on_ready(self):
        setup_logging()
        self.ge.on_ready(self)
        await self.general.sendMessageToDefaultChannels(self, 'เด็กข้างไข่ออนไลน์แล้วค้าบ', delete_after=True)
        
    def add_commands(self):
        @self.command(name="p", pass_context=True)
        async def text2speech(contex):
            voiceClinet = await self.t2p.connect(self, contex)
            await self.t2p.play(self, contex)
            await self.at.setCountdownDisconnect(voiceClinet)
            
        @self.command(pass_context=True)
        async def connect(contex):
            voiceClinet = await self.t2p.connect(self, contex)
            await self.at.setCountdownDisconnect(voiceClinet)
        
        @self.command(pass_context=True)
        async def disconnect(contex):
            await self.t2p.disconnect(self, contex)
        
        @self.command(pass_context=True)
        async def register(contex):
            await self.ds.register(contex)

        @self.command(pass_context=True)
        async def daily(contex):
            await self.ds.daily(contex)

        @self.command(pass_context=True)
        async def check(contex):
            await self.ds.check(contex)

        @self.command(pass_context=True)
        async def send(contex, receiver: discord.User, amount):
            try:
                Decimal(amount)
                await self.ds.send(contex, receiver, Decimal(amount))
            except ValueError:
                await contex.send("<@{}> ใส่ค่าจำนวนเงินที่ส่งเป็นเลขจำนวนจริง และ ต้องมากว่า 0.00"
                                    .format(str(contex.author._user.id)), 
                                    delete_after=get_settings().SELF_MESSAGE_DELETE_TIME)
                return 
            except Exception as e:
                logging.error(f'[Bot.send] : {e}')
                await contex.send("<@{}> คำสั่งเกิดข้อผิดพลาดกรุณาใส่ .send @[ผู้รับเงิน] [จำนวนเงินที่ให้ (เลขจำนวนจริงที่มากว่า 0)]"
                                    .format(str(contex.author._user.id)), 
                                    delete_after=get_settings().SELF_MESSAGE_DELETE_TIME)
                return 

        @self.command(pass_context=True)
        async def bet(contex, amount):
            try:
                Decimal(amount)
                await self.ds.bet(contex, Decimal(amount))
            except ValueError:
                await contex.send("<@{}> ใส่ค่าเดิมพันเป็นเลขจำนวนจริง และ ต้องมากว่า 0.00"
                                    .format(str(contex.author._user.id)), 
                                    delete_after=get_settings().SELF_MESSAGE_DELETE_TIME)
                return 

            except Exception as e:
                logging.error(f'[Bot.bet] : {e}')
                await contex.send("<@{}> คำสั่งเกิดข้อผิดพลาดกรุณาใส่ .bet [เงินเดิมพัน (เลขจำนวนจริงที่มากว่า 0)]"
                                    .format(str(contex.author._user.id)), 
                                    delete_after=get_settings().SELF_MESSAGE_DELETE_TIME)
                return 

        @self.command(pass_context=True)
        async def hourly(contex):
            await self.ds.hourly(contex)

        @self.command(name = 'default', pass_context=True)
        async def setDefaultChannel(contex):
            await self.ds.createOrUpdateDefualtChannel(contex, str(contex.message.guild.id), str(contex.message.channel.id))
