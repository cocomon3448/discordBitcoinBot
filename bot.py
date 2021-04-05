import discord
from discord.ext import commands
import hashlib
import time
import random
import re

client = commands.Bot(command_prefix='!')

@client.event
async def on_ready():
    print("Bot is online")

class Block:

    def __init__(self, index, proof_no, prev_hash, data, timestamp=None):
        self.index = index
        self.proof_no = proof_no
        self.prev_hash = prev_hash
        self.data = data
        self.timestamp = timestamp or time.time()

    @property
    def calculate_hash(self):
        block_of_string = "{}{}{}{}{}".format(self.index, self.proof_no,
                                              self.prev_hash, self.data,
                                              self.timestamp)

        return hashlib.sha256(block_of_string.encode()).hexdigest()

    def __repr__(self):
        return "{} - {} - {} - {} - {}".format(self.index, self.proof_no,
                                               self.prev_hash, self.data,
                                               self.timestamp)


class BlockChain:

    def __init__(self):
        self.chain = []
        self.current_data = []
        self.nodes = set()
        self.construct_genesis()

    def construct_genesis(self):
        self.construct_block(proof_no=random.randint(0,1000000), prev_hash=random.randint(0,1000000))

    def construct_block(self, proof_no, prev_hash):
        block = Block(
            index=len(self.chain),
            proof_no=proof_no,
            prev_hash=prev_hash,
            data=self.current_data)
        self.current_data = []

        self.chain.append(block)
        return block

    @staticmethod
    def check_validity(block, prev_block):
        if prev_block.index + 1 != block.index:
            return False

        elif prev_block.calculate_hash != block.prev_hash:
            return False

        elif not BlockChain.verifying_proof(block.proof_no,
                                            prev_block.proof_no):
            return False

        elif block.timestamp <= prev_block.timestamp:
            return False

        return True

    def new_data(self, sender, recipient, quantity):
        self.current_data.append({
            'sender': sender,
            'recipient': recipient,
            'quantity': quantity
        })
        return True

    @staticmethod
    def proof_of_work(last_proof):
        '''this simple algorithm identifies a number f' such that hash(ff') contain 4 leading zeroes
         f is the previous f'
         f' is the new proof
        '''
        proof_no = 0
        while BlockChain.verifying_proof(proof_no, last_proof) is False:
            proof_no += 1

        return proof_no

    @staticmethod
    def verifying_proof(last_proof, proof):
        #verifying the proof: does hash(last_proof, proof) contain 4 leading zeroes?

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    @property
    def latest_block(self):
        return self.chain[-1]

    def block_mining(self, details_miner):

        self.new_data(
            sender="0",  #it implies that this node has created a new block
            receiver=details_miner,
            quantity=
            1,  #creating a new block (or identifying the proof number) is awarded with 1
        )

        last_block = self.latest_block

        last_proof_no = last_block.proof_no
        proof_no = self.proof_of_work(last_proof_no)

        last_hash = last_block.calculate_hash
        block = self.construct_block(proof_no, last_hash)

        return vars(block)

    def create_node(self, address):
        self.nodes.add(address)
        return True

    @staticmethod
    def obtain_block_object(block_data):
        #obtains block object from the block data

        return Block(
            block_data['index'],
            block_data['proof_no'],
            block_data['prev_hash'],
            block_data['data'],
            timestamp=block_data['timestamp'])


@client.command()
async def ping(ctx):
    ping = round(client.latency * 1000)
    if ping > 1 and ping < 100:
        statu = 'Very Good'
    if ping > 101 and ping < 200:
        statu = 'Not Bad'
    else:
        statu = 'Slow'
    await ctx.send(f'Ping is {ping} ms ({statu})')

@client.command()
async def kick(ctx, member : discord.Member,*,reason=None):
    await member.kick(reason=reason)
@client.command()
async def ban(ctx, member : discord.Member,*,reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'Banned {member.mention}')
###################################################################

blockchain = BlockChain()

print(blockchain.chain)

last_block = blockchain.latest_block
last_proof_no = last_block.proof_no
proof_no = blockchain.proof_of_work(last_proof_no)

blockchain.new_data(
    sender="0",  #it implies that this node has created a new block
    recipient="Server I think?",  #let's send Quincy some coins!
    quantity=1,
)
user = ''
last_hash = last_block.calculate_hash
block = blockchain.construct_block(proof_no, last_hash)
print(proof_no)
newblock = True
@client.command()
async def mine(ctx, *,nonce):
    global newblock
    global proof_no
    global last_hash
    if newblock == False:
        last_block = blockchain.latest_block
        last_proof_no = last_block.proof_no
        proof_no = blockchain.proof_of_work(last_proof_no)
        last_hash = last_block.calculate_hash
        block = blockchain.construct_block(proof_no, last_hash)
        print(proof_no)
        newblock = True
    if int(nonce) == proof_no:
        await ctx.send('Mined Block!!')
        user_data = '{0.author.mention}'.format(ctx.message)
        print(user_data)
        with open("data.txt", "r+") as f:
            old = f.read() # read everything in the file
            f.seek(0) # rewind
            data = "{0}:1".format(user_data)
            f.write(data+"\n" + old) # write the new line before
        newblock = False
    elif int(nonce) != int(proof_no):
        await ctx.send('Nope')

@client.command(pass_context=True)
async def asset(ctx,*,username):
    global user
    username = re.sub(r"[^a-zA-Z0-9]","",username)
    with open('data.txt') as f:
        lines = f.readlines()
        user = [line.rstrip() for line in lines if line.find(username)]
        print(user[0], username)
    # 문제 - restrip() 작동 오류인듯하다.
    # 문제 - list 에 split() 함수 적용이 안된다.
    # 문제 - !asset 명령어 대안이 없다.
    strings = user[0].split(':')
    user = []
    print(strings)
    asset = str(strings[1])
    print(asset)
    username = '<@'+username+'>'
    print(username, strings[0])
    if username == strings[0]:
        await ctx.send(f'{username}의 자산 => 비트코인 {asset}개')
    
###############################################################
# @client.command()
# async def asset(ctx.*,username):


# @client.command()
# async def clear(ctx, amount=3):
#     await ctx.channel.purge(limit=amount)
# @client.events
# async def on_member_join(member):
#     print(f'{member} has joined a server')

# @client.event
# async def on_member_remove(member):
#     print(f'{member} has left server')

client.run('your oauth')
