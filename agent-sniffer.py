from ast import arg
import os
import discord
from discord.ext import commands
import urllib.request
import json
import certifi
import ssl
from prettytable import PrettyTable
from quickchart import QuickChart
from table2ascii import table2ascii as t2a, PresetStyle,Alignment

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID_DEFAULT = os.getenv('GUILD_ID')
MY_GUILD = []
BRAWL_ID = ""
guild = []
# client = discord.Client()
client = commands.Bot(command_prefix='!')

def get_guild_id(id):
    id = id.replace('\"', '')
    api_url = "https://api2.splinterlands.com/guilds/list?v=1654693615472"
    with urllib.request.urlopen(
            api_url,
            context=ssl.create_default_context(cafile=certifi.where())) as url:
        data = json.loads(url.read().decode())
    return [i['id'] for i in data if i['name'] == id][0]

def testChart():
  embed=discord.Embed(title="Guild Brawl", url="https://realdrewdata.medium.com/", description="This is an embed that will show how to build an embed and the different components", color=0xFF5733)

  
  
  qc = QuickChart()
  qc.width = 500
  qc.height = 300
  qc.device_pixel_ratio = 2.0
  qc.config = {
      "type": "bar",
      "data": {
          "labels": ["Hello world", "Test"],
          "datasets": [{
              "data": [1, 2]
          }]
      }
  }

  # Print the chart URL
  print(qc.get_url())
  embed.set_image(url=qc.get_url())
  return embed

def get_card_info(id):
    file = open('cards.json')
    cards = json.load(file)
    file.close()
    return [i["name"] for i in cards if i["id"] == id][0]

#initialize data
def init_data(guild_id):
    global guild
    global BRAWL_ID
    global MY_GUILD

    guild = []
  
    api_url = "https://api2.splinterlands.com/guilds/find?id=" + guild_id
    with urllib.request.urlopen(
            api_url,
            context=ssl.create_default_context(cafile=certifi.where())) as url:
        data = json.loads(url.read().decode())
        MY_GUILD = data
        BRAWL_ID = data["tournament_id"]
    api_url = "https://api2.splinterlands.com/tournaments/find_brawl?id=" + BRAWL_ID + "&guild_id=" + guild_id
    #get brawl participants
    with urllib.request.urlopen(
            api_url,
            context=ssl.create_default_context(cafile=certifi.where())) as url:
        data = json.loads(url.read().decode())
        for i in data["guilds"]:
            guild.append(i)

    return guild

#get fray data
def get_fray_data(guild,fray):
  fray = int(fray)
  player_list=[]
  
  for guild in guild:
      api_url = "https://api2.splinterlands.com/tournaments/find_brawl?id="+BRAWL_ID+"&guild_id="+guild['id']+"&v=1652052902612"

      with urllib.request.urlopen(api_url, context=ssl.create_default_context(cafile=certifi.where())) as url:
                  data = json.loads(url.read().decode())
                  players = data["players"]

      myTable = PrettyTable()
      myTable.title = guild["name"]
      myTable.field_names = ["Player", "Fray", "Rating", "Power"]
      for i in players:
          player_list.append({
              "fray":int(i["fray_index"])+1,
              "player":i["player"],
              "guild":guild["name"],
              "total_battles": i["total_battles"],
              "entered_battles": i["entered_battles"],
              "wins": i["wins"],
              "losses": i["losses"],
              "draws": i["draws"],
              "cp":i["player_data"]["collection_power"]
          })
          myTable.add_row([
              i["player"],
              str(int(i["fray_index"])+1),
              str(i["player_data"]["rating"]),
              str(i["player_data"]["collection_power"])
              ])

      #print(myTable)
  # myTable = PrettyTable()
  # myTable.title ="FRAY 1"
  # myTable.field_names = ["Player", "Guild","Entered Battles"]
  # for k in [i for i in player_list if i["fray"] == 1]:
  #     myTable.add_row([
  #         k["player"],
  #         k["guild"],
  #         str(k["entered_battles"]) + "/" + str(k["total_battles"])
  #     ])
  # print(myTable)

  for j in range(fray,fray+1):
      myTable = PrettyTable()
      myTable.title ="FRAY " + str(j)
      myTable.field_names = ["Player", "Guild","CP","Entered Battles","Wins","Losses","Draws"]
      for k in [i for i in player_list if i["fray"] == j]:
          myTable.add_row([
              k["player"],
              k["guild"],
              k["cp"],
              str(k["entered_battles"]) + "/" + str(k["total_battles"]),
              k["wins"],
              k["losses"],
              k["draws"]
          ])

  return myTable

def get_guild_data(guild):
    guild_data = []
    for guild in guild:
      api_url = "https://api2.splinterlands.com/guilds/find?id="+guild["id"]
        
      with urllib.request.urlopen(api_url, context=ssl.create_default_context(cafile=certifi.where())) as url:
        data = json.loads(url.read().decode())
        guild_data.append(data)
        
    for i in guild_data:
      i["buildings"] = json.loads(i["buildings"])
    
    test = []
    for i in guild_data:
      if i["buildings"]["barracks"]["level"] > 2:
        blocked_card = get_card_info(i["buildings"]["barracks"]["away_blocked_cards"][0])
      else:
        blocked_card = "N/A"
      if i["name"] == "🐕L1L Dawgs Elite - LDG🐕":
        i["name"] = i["name"][1:-1]
        
      test.append([
        i["name"],
        i["level"],
        i["rank"],
        i["brawl_level"],
        i["buildings"]["barracks"]["level"],
        blocked_card
        ])
      output = t2a(
            header = ["Guildname", "Guild Hall", "Rank", "Brawl LVL", "Barracks","Blocked Card"],
            body=test,
            alignments=[
              Alignment.LEFT, 
              Alignment.CENTER, 
              Alignment.CENTER,
              Alignment.CENTER,
              Alignment.CENTER,
              Alignment.CENTER
            ],
            style=PresetStyle.thin_compact
            ),
            

    return output

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.command()
async def brawl(ctx, *args):
    channel = ctx.message.channel

    if str(channel) == 'agent-orange-test-thread' or str(channel) == '🐕｜agent-sniffer-dawg':
        #init_data()
        if len(args) == 0:
            #await ctx.channel.send(f'Welcome to {MY_GUILD["name"]}!!!')
            guild = init_data(GUILD_ID_DEFAULT)
            await ctx.reply('```\n%s\n```' % (get_guild_data(guild)),)
            print(channel)

        elif len(args) == 1 and args[0] == "fray":
          await ctx.reply("Include your fray number. Ex. !brawl fray 1")
        elif len(args)>1 and args[0] == "fray":    
          guild = init_data(GUILD_ID_DEFAULT)
          
          await ctx.reply("```\n%s\n```" % (get_fray_data(guild,args[1])))
        
        elif len(args) == 1 and args[0] != "stat" :
            GUILD_ID = get_guild_id(args[0])
            print(GUILD_ID)
            guild = init_data(GUILD_ID)
            await ctx.reply('```\n%s\n```' % (get_guild_data(guild)),)
            print(channel)

            

        elif args[0] == "stat" and len(args) == 1:
            embed = testChart()
            await ctx.reply(embed=embed)
            # await ctx.channel.send(f'brawl!!!')

        elif args[0] == "stat" and args[1] == "stat":
            embed = testChart()
            await ctx.reply(embed=embed)
            await ctx.reply(embed=embed)
            # await ctx.channel.send(f'brawl!!!')

client.run(TOKEN)
