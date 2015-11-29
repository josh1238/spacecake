#!/usr/bin/env python
"""
This is a module for bot commands so that bot.py can import them.
Commands are split into seperate classes.
"""

addrls = ['slap']
ls = []

def AddrFuncs(cmd, args, data, conn):
  if cmd == 'slap':
    target = args[0]
    slappee = data['sender']
    chan = data['channel']
    msg = "slaps %s with a floppy fish, then points at %s" % (target, slappee)
    conn.describe(msg, chan)

def UnAddrFuncs(cmd, args, data, conn):
  ls = []

def OnJoinFuncs(channel):
  pass

def OtherJoinFuncs(data):
  pass

def OnKickedFuncs(msg, data):
  pass

def OtherKickedFuncs(msg, data):
  pass
