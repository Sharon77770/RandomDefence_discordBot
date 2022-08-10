from cmath import inf
from json.encoder import INFINITY
import discord
import os
from random import *
from discord.ext.commands import Bot
from discord.utils import get
from urllib import request
from bs4 import BeautifulSoup

intents = discord.Intents.default()
intents.members = True
bot = Bot(command_prefix='!', intents=intents)

class Values:
    game_is_started = False

    user_list = {}
    user_problems = {}

    master_id = 781160097434435625
    developer_id = 759943384193826856

    game_channel_id = 984555869607960580
    scoreboard_channel_id = 984882001813319750

    url_baekjoon = {
        'https://www.acmicpc.net/status?problem_id=',
        '&user_id=',
        '&language_id=-1&result_id=-1'
    }



class Utillity:
    @staticmethod
    def set_score(before_score):
        cnt = 0
        user_id = ''
        at_time = 0
        at_score = 0
        de_score = 0

        for info in before_score.split("\n"):
            if info == '':
                continue
            if info == 'SCORE':
                continue
            
            if cnt == 0: user_id = info
            elif cnt == 1: at_time = int(info.split(': ')[1])
            elif cnt == 2: at_score = int(info.split(': ')[1])
            elif cnt == 3: de_score = int(info.split(': ')[1])
            cnt += 1

            if cnt == 4:
                Values.user_list[user_id] = { 'at_time': at_time, 'at_score': at_score, 'de_score': de_score }
                cnt = 0

    @staticmethod
    def show_score():
        msg = ''
        for user_id in Values.user_list:
            msg += '{}\n공격횟수: {}\n공격점수: {}\n수비점수: {}\n\n'.format(user_id, Values.user_list[user_id]['at_time'], Values.user_list[user_id]['at_score'], Values.user_list[user_id]['de_score'])
        return msg

    @staticmethod
    def make_embed():
        embed = discord.Embed(title="SCORE", color=0x62c1cc) 
        for user_id in Values.user_list:
            embed.add_field(name=user_id, value=f'공격횟수: {Values.user_list[user_id]["at_time"]}\n공격점수: {Values.user_list[user_id]["at_score"]}\n수비점수: {Values.user_list[user_id]["de_score"]}', inline=False)
        return embed

    @staticmethod
    def check_solved(attecker, problem):
        target = request.urlopen('https://www.acmicpc.net/status?problem_id={}&user_id={}&language_id=-1&result_id=4'.format(problem, attecker))
        soup = BeautifulSoup(target,'html.parser')
        t = soup.find_all('a', { 'href' : '/user/{}' .format(attecker) })
        if t.__len__() == 0:
            return False
        
        return True

    @staticmethod
    def get_problem_tier(problem):
        target = request.urlopen('https://solved.ac/search?query={}'.format(problem))
        soup = BeautifulSoup(target,'html.parser')
        t = soup.find('a', { 'href': 'https://www.acmicpc.net/problem/{}'.format(problem) })
        msg = str(t)
        msg = msg.split('alt="')[1].split('"')[0]
        if msg == 'Sprout':
            return 'Bronze V'
        return msg

    @staticmethod
    def get_user_tier(user_id):
        target = request.urlopen('https://solved.ac/search/users?query={}'.format(user_id))
        soup = BeautifulSoup(target,'html.parser')
        t = soup.find('img', { 'class' : 'css-1vnxcg0' })
        msg = str(t)
        msg = msg.split('alt="')[1].split('"')[0]
        if msg == 'Sprout':
            return 'Bronze V'
        return msg

    @staticmethod
    def tier_to_num(tier):
        ret = 0

        if tier.split(' ')[0] == 'Bronze': ret += 100
        elif tier.split(' ')[0] == 'Silver': ret += 200
        elif tier.split(' ')[0] == 'Gold': ret += 300
        elif tier.split(' ')[0] == 'Platinum': ret += 400
        elif tier.split(' ')[0] == 'Diamond': ret += 500
        elif tier.split(' ')[0] == 'Ruby': ret += 600

        if tier.split(' ')[1] == 'I': ret += 5
        elif tier.split(' ')[1] == 'II': ret += 4
        elif tier.split(' ')[1] == 'III': ret += 3
        elif tier.split(' ')[1] == 'IV': ret += 2
        elif tier.split(' ')[1] == 'V': ret += 1

        return ret

    @staticmethod
    def get_user_try_time(user_id, problem):
        ret = 0
        for i in range(4, 12):
            target = request.urlopen('https://www.acmicpc.net/status?problem_id={}&user_id={}&language_id=-1&result_id={}'.format(problem, user_id, i))
            soup = BeautifulSoup(target,'html.parser')
            t = soup.find_all('a', { 'href' : '/user/{}' .format(user_id) })
            ret += t.__len__()
        return ret



@bot.event
async def on_ready():
    await bot.get_channel(Values.game_channel_id).send('봇이 재실행 되었습니다.점수는 기록되었지만 이전에 공격했던 기록은 남지 않습니다.\n개발자 또는 서버장이 "!START &(이전 게임 점수판 복붙)"을 입력하기 전까진 봇이 작동하지 않습니다.')

@bot.command()
async def START(ctx):
    if ctx.channel.id != Values.game_channel_id:
        return
    if Values.game_is_started == True:
        await ctx.send('이미 게임이 진행중입니다.')
        return
    if ctx.author.id == Values.master_id or ctx.author.id == Values.developer_id:
        if ctx.message.content.split(' ').__len__() == 1:
            await ctx.send(f'{ctx.author.mention}점수판을 복사해주세요.')
            return

        Values.game_is_started = True

        before_score = ctx.message.content.split('&')[1]
        Utillity.set_score(before_score)

        await bot.get_channel(Values.game_channel_id).send(f'{ctx.author.mention}게임이 시작되었습니다.')
        await bot.get_channel(Values.scoreboard_channel_id).purge(limit=1)
        await bot.get_channel(Values.scoreboard_channel_id).send(embed=Utillity.make_embed())
    else:
        await bot.get_channel(Values.game_channel_id).send(f'{ctx.author.mention}개발자 또는 서버장이 시작해야 합니다.')

@bot.command()
async def join(ctx):
    if ctx.channel.id != Values.game_channel_id:
        return
    if Values.game_is_started == False:
        await ctx.send(f'{ctx.author.mention}게임이 시작되지 않았습니다.')
        return
    if ctx.author.display_name in Values.user_list:
        await ctx.send('이미 참여하셨습니다.')
        return

    Values.user_list[ctx.author.display_name] = { 'at_time': 0 , 'at_score': 0, 'de_score': 0 }
    await ctx.send(f'{ctx.author.mention}님이 랜덤 디펜스에 참가하셨어요.')
    await bot.get_channel(Values.scoreboard_channel_id).purge(limit=1)
    await bot.get_channel(Values.scoreboard_channel_id).send(embed=Utillity.make_embed())
    
@bot.command()
async def attack(ctx):
    if ctx.channel.id != Values.game_channel_id:
        return
    if Values.game_is_started == False:
        await ctx.send(f'{ctx.author.mention}게임이 시작되지 않았습니다.')
        return
    if ctx.message.content.split(' ').__len__() != 4:
        await ctx.send(f'{ctx.author.mention} "!attack 대상의백준id 문제번호 제출횟수" 형식을 지켜서 공격해주세요.')
        return
    if int(ctx.message.content.split(' ')[3]) < 3:
        await ctx.send(f'{ctx.author.mention} 제출횟수는 3회 이상이어야 합니다.')
        return

    defender_name = ctx.message.content.split(' ')[1]

    if ctx.author.display_name == defender_name:
        await ctx.send(f'{ctx.author.mention}자신을 공격할 수 없습니다.')
        return
    if ctx.author.display_name not in Values.user_list:
        await ctx.send(f'{ctx.author.mention}님은 참가하지 않았습니다.')
        return
    if defender_name not in Values.user_list:
        await ctx.send(f'{ctx.author.mention}공격 대상이 게임에 참가하지 않았거나 대상의 백준 아이디가 잘못 됐습니다.')
        return
    
    if defender_name in Values.user_problems:
        for problem in Values.user_problems[defender_name]:
            if problem == None:
                break
            if problem['number'] == ctx.message.content.split(' ')[2]:
                await ctx.send(f'{ctx.author.mention}누군가가 이미 공격한 문제입니다.')
                return
    else:
        Values.user_problems[defender_name] = []

    if Values.user_problems[defender_name].__len__() >= 5:
        await ctx.send(f'{ctx.author.mention}공격 대상이 진행중인 문제가 너무 많습니다.')
        return

    ut1 = Utillity.tier_to_num(Utillity.get_user_tier(defender_name))
    pt1 = Utillity.tier_to_num(Utillity.get_problem_tier(ctx.message.content.split(' ')[2]))

    if ut1 < pt1:
        await ctx.send(f'{ctx.author.mention}공격 대상의 티어 이하의 문제만 사용할 수 있습니다.')
        return

    if Utillity.check_solved(ctx.author.display_name, ctx.message.content.split(' ')[2]) == False:
        await ctx.send(f'{ctx.author.mention} 문제를 풀지 않았습니다.')
        return

    if Utillity.check_solved(defender_name, ctx.message.content.split(' ')[2]) == True:
        await ctx.send(f'{ctx.author.mention} 대상이 이미 문제를 풀었습니다.')
        return

    members = [member for member in ctx.guild.members]

    for member in members:
        if member.display_name == defender_name:
            await ctx.send('{}님이 {}님을 공격했습니다. 해당 문제를 푸는 도중엔 해당 문제를 질문을 할수 없습니다.'.format(ctx.author.mention, member.mention))
            await ctx.send('https://www.acmicpc.net/problem/{}'.format(ctx.message.content.split(' ')[2]))
            break

    Values.user_list[ctx.author.display_name]['at_time'] = Values.user_list[ctx.author.display_name]['at_time'] + 1
    Values.user_problems[defender_name].append({ 'attacker': ctx.author.display_name, 'number': ctx.message.content.split(' ')[2], 'time': ctx.message.content.split(' ')[3], 'defulte' : Utillity.get_user_try_time(defender_name, ctx.message.content.split(' ')[2]) })
    await bot.get_channel(Values.scoreboard_channel_id).purge(limit=1)
    await bot.get_channel(Values.scoreboard_channel_id).send(embed=Utillity.make_embed())

@bot.command()
async def problems(ctx):
    if ctx.channel.id != Values.game_channel_id:
        return
    if Values.game_is_started == False:
        await ctx.send(f'{ctx.author.mention}게임이 시작되지 않았습니다.')
        return
    if ctx.author.display_name not in Values.user_list:
        await ctx.send(f'{ctx.author.mention}님은 참가하지 않았습니다.')
        return
    if ctx.author.display_name not in Values.user_problems:
        await ctx.send(f'{ctx.author.mention}님은 아직 푼 문제가 없습니다.')
        return       
    if Values.user_problems[ctx.author.display_name].__len__() == 0:
        await ctx.send(f'{ctx.author.mention}님은 아직 푼 문제가 없습니다.')
        return

    await ctx.send(f'{ctx.author.mention}님의 방어문제들은 아래와 같습니다.')

    msg = ''
    msg_p = ''

    for problem in Values.user_problems[ctx.author.display_name]:
        left_time = int(problem['time']) -  Utillity.get_user_try_time(ctx.author.display_name, problem['number']) + problem['defulte']
        if left_time <= 0:
            msg_p += '-{}번 문제\n공격자: {}\n\n'.format(problem['number'], problem['attacker'])
            Values.user_list[problem['attacker']]['at_score'] += 1
            Values.user_list[ctx.author.display_name]['de_score'] -= 1
            Values.user_problems[ctx.author.display_name].remove(problem)
        else:
            msg += '-{}번 문제\n남은 제출 횟수: {}회\nhttps://www.acmicpc.net/problem/{}\n\n'.format(problem['number'], left_time, problem['number'])
    
    if msg_p != '':
        msg += f'{ctx.author.mention}확인중 실패한 문제가 발견되었습니다. 문제는 아래와 같습니다.\n' + msg_p
        await bot.get_channel(Values.scoreboard_channel_id).purge(limit=1)
        await bot.get_channel(Values.scoreboard_channel_id).send(embed=Utillity.make_embed())

    await ctx.send(msg)
    
@bot.command()
async def delete(ctx):
    if ctx.channel.id != Values.game_channel_id:
        return
    if Values.game_is_started == False:
        await ctx.send(f'{ctx.author.mention}게임이 시작되지 않았습니다.')
        return
    if ctx.author.id == Values.master_id or ctx.author.id == Values.developer_id:
        if ctx.message.content.split(' ').__len__() != 2:
            await ctx.send(f'{ctx.author.mention} "!delete 대상의백준id" 형식을 지켜서 삭제해주세요.')
            return

        if ctx.message.content.split(' ')[1] not in Values.user_list:
            await ctx.send(f'{ctx.author.mention}삭제 대상이 게임에 참가하지 않았거나 대상의 백준 아이디가 잘못 됐습니다.')
            return

        Values.user_list.pop(ctx.message.content.split(' ')[1])
        if ctx.message.content.split(' ')[1] in Values.user_problems:
            Values.user_problems.pop(ctx.message.content.split(' ')[1])
        await ctx.send(f'{ctx.author.mention}삭제가 완료되었습니다.')

        await bot.get_channel(Values.scoreboard_channel_id).purge(limit=1)
        await bot.get_channel(Values.scoreboard_channel_id).send(embed=Utillity.make_embed())

    else:
        await ctx.send(f'{ctx.author.mention}개발자 또는 서버장이 아닙니다.')

@bot.command()
async def clear(ctx):
    if ctx.channel.id != Values.game_channel_id:
        return
    if Values.game_is_started == False:
        await ctx.send(f'{ctx.author.mention}게임이 시작되지 않았습니다.')
        return
    if ctx.author.display_name not in Values.user_list:
        await ctx.send(f'{ctx.author.mention}님은 참가하지 않았습니다.')
        return
    if ctx.author.display_name not in Values.user_problems:
        await ctx.send(f'{ctx.author.mention}해결된 문제가 없습니다.')
        return

    members = [member for member in ctx.guild.members]
    msg = ''
    is_r = True

    for problem in Values.user_problems[ctx.author.display_name]:
        if Utillity.check_solved(ctx.author.display_name, problem['number']) == True:
            left_time = int(problem['time']) -  Utillity.get_user_try_time(ctx.author.display_name, problem['number']) + problem['defulte']
            
            if left_time < 0:
                is_r = False
                continue

            for member in members:
                if member.display_name == problem['attacker']:
                    msg += '{}님의 문제를 해결했습니다!\n'.format(member.mention)
                    break
            Values.user_list[ctx.author.display_name]['de_score'] += 1
            Values.user_problems[ctx.author.display_name].remove(problem)

    if is_r == False:
        await ctx.send(msg + f'\n{ctx.author.mention}해결한 문제중 만료 된 문제가 있습니다. !problems 명령어를 사용해서 확인해주세요.')
        return
    if msg == '':
        await ctx.send(f'{ctx.author.mention}해결된 문제가 없습니다.')
        return
    await ctx.send(msg)
    await bot.get_channel(Values.scoreboard_channel_id).purge(limit=1)
    await bot.get_channel(Values.scoreboard_channel_id).send(embed=Utillity.make_embed())
    
@bot.command()
async def surrender(ctx):
    if ctx.channel.id != Values.game_channel_id:
        return

    if ctx.message.content.split(' ').__len__() != 2:
        await ctx.send(f'{ctx.author.mention} "!surrender 문제번호" 형식을 지켜주세요.')

    if ctx.author.display_name not in Values.user_problems:
        await ctx.send(f'{ctx.author.mention}삭제 대상이 잘못 됐습니다.')
        return

    target = ctx.message.content.split(' ')[1]

    for problem in Values.user_problems[ctx.author.display_name]:
        if problem['number'] == target:
            await ctx.send(f'{ctx.author.mention}문제가 삭제되었습니다.')
            Values.user_list[problem['attacker']]['at_score'] += 1
            Values.user_list[ctx.author.display_name]['de_score'] -= 1
            Values.user_problems[ctx.author.display_name].remove(problem)
            return

    await ctx.send(f'{ctx.author.mention}삭제 대상이 잘못 됐습니다.')

@bot.command()
async def how(ctx):
    if ctx.channel.id != Values.game_channel_id:
        return
    msg =  ctx.author.mention+'사용 가능한 명령어는 다음과 같습니다.\n\n'
    msg += '!join : 랜덤디펜스에 참가합니다\n'
    msg += '!attack 공격대상 문제번호 제출제한횟수 : 대상을 공격합니다\n'
    msg +='!problems : 문제를 확인합니다. 확인과정에서 만료된 문제는 삭제합니다.\n'
    msg += '!clear : 해결한 문제를 삭제합니다.\n'
    msg += '!surrender 문제번호 : 해당 문제를 삭제합니다. 이 경우에 공격자의 점수가 오릅니다.\n'

    await ctx.send(msg)
    
bot.run(os.environ['token'])