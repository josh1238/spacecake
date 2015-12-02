#!/usr/bin/env python
# coding=utf-8
"""
This is a module for bot commands so that bot.py can import them.
Commands are if statements within functions. The ls tables let bot.py know that the command exists.
"""

addrls = ['act','speak','quit','slap','die']
ls = ['!help','.help','!unflip','.unflip','!flip','.flip','^5']

def AddrFuncs(cmd, args, data, conn):
  chan = data['channel']
  if cmd == 'slap':
    target = args[0]
    slappee = data['sender'].split('!')[0]
    msg = "slaps %s with a floppy fish, then points at %s" % (target, slappee)
    conn.describe(msg, chan)
  elif cmd == 'act':
    chan = args[0]
    msg = ' '.join(args[1:])
    conn.describe(msg, chan)
  elif cmd == 'speak':
    chan = args[0]
    msg = ' '.join(args[1:])
    conn.say(msg, chan)
  elif cmd == 'quit':
    asker = data['sender'].split('!')[0]
    if asker == 'josh1238':
      conn.quit('shutting down')
    else:
      conn.say('┌∩┐(ಠ_ಠ)┌∩┐'.decode('utf-8'), chan)
  elif cmd == 'die':
    conn.say('nou', chan)

def UnAddrFuncs(cmd, args, data, conn):
  chan = data['channel']
  if cmd == '!help' or cmd == '.help':
    conn.say("happypizza doesn't want to help you", chan)
  if cmd == '!flip' or cmd == '.flip':
    conn.say('(ノ°▽°)ノ︵┻━┻'.decode('utf-8'), chan)
  elif cmd == '!unflip' or cmd == '.unflip':
    conn.say('┬─┬ノ(°▽°ノ)'.decode('utf-8'), chan)
  elif cmd == '^5':
    fiver = data['sender'].split('!')[0]
    chan = data['channel']
    msg = "high fives %s in the face" % fiver
    conn.describe(msg, chan)

def OnJoinFuncs(channel, conn):
  pass

def OtherJoinFuncs(data, conn):
  if data['nick'] == 'zeezey':
    conn.say('( ´・ω・)つ──☆✿✿✿✿✿✿ Welcome to the channel zeezey!'.decode('utf-8'), data['channel'])
  else:
    conn.say('Hi my name is spacecake', data['channel'])

def OnKickedFuncs(msg, data, conn):
  pass

def OtherKickedFuncs(msg, data, conn):
  chan = data['channel']
  conn.say('╭∩╮ʕ•ᴥ•ʔ╭∩╮'.decode('utf-8'), chan)
