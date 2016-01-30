#!/usr/bin/env python
# coding=utf-8
import time
import sys
import socket
import threading
import com
from imp import reload
from ident import freenode
#from ident import efnet

def colorize(text, color):
  """
  Adds color (code @color) to text @text, which can then be embedded in a
  message.
  """
  # \x03<zero-padded-to-width-2-color><text>\x03
  return "\x03%02d%s\x03" % (color, text)

def bold(text):
  """
  Returns text @text with bold formatting, which can then be embedded in a
  message.
  """
  # \x02<text>\x02
  return "\x02%s\x02" % text

def underline(text):
  """
  Returns text @text with underline formatting, which can then be embedded in 
  a message.
  """
  # \x1f<text>\x1f
  return "\x1f%s\x1f" % text

class IRCConn(object):
  """
  This class handles the connection with the IRC server.
  It connects and sends and receives messages.
  """

  #### Initializers ####
  def __init__(self, handler):
    self.handler = handler
    i = handler.ident
    self.ident = i['ident']
    self.host = i['host']
    self.name = i['real_name']
    self.nick = i['nick']
    self.join_first = i['chan']
    self.port = i['port']
    self.connected = False
    self.channels = set()
    self.nicks = {}

  def connect(self):
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.settimeout(600)
    self.sock.connect((self.host, self.port))
    self.connected = True
    self._send("USER %s %s %s :%s" % (self.ident, '0', '*', self.name))
    self._send("NICK %s" % self.nick)
    # wait until we have received the MOTD in full before proceeding
    self.mainloop()

  def mainloop(self):
    """
    The mainloop
    """
    # Rather than while True: for speed
    while self.connected:
      line = self.receive()
      thredd = threading.Thread(target=self.parse, args=(line,))
      thredd.start()

  #### Commands ####
  def say(self, msg, chan, to=None):
    """
    Say @msg on @chan
    """
    if to is None:
      prefix = ''
    else:
      prefix = "%s: " % to

    for line in msg.splitlines():
      self._send("PRIVMSG %s :%s%s" % (chan, prefix, line))

  def whois(self, nick):
    """
    Send a WHOIS command for nick @nick.
    """
    self._send("WHOIS %s" % nick)

  def who(self, chan_nick):
    """
    Send a WHO command for nick or channel @chan_nick.
    """
    self._send("WHO %s" % chan_nick)

  def names(self, chan):
    """
    Send a NAMES command for channel @chan.
    """
    self._send("NAMES %s" % chan)

  def ident(self, pswd):
    """
    Do a NickServ identify with @pswd.
    """
    self.say("identify %s" % pswd, "NickServ")

  def describe(self, msg, chan):
    """
    Describe the user as doing @msg on channel @chan.
    """
    self.say("\x01ACTION %s\x01" % msg, chan)

  def mode(self, mode, mask, chan):
    """
    Set mode @mode for mask @mask on channel @channel.
    """
    self._send("MODE %s %s %s" % (chan, mode, mask))

  # A few common mode shortcuts
  def ban(self, mask, chan):
    """
    Ban mask @mask from channel @chan.
    """
    self.mode('+b', mask, chan)

  def unban(self, mask, chan):
    """
    Unban mask @mask from channel @chan.
    """
    self.mode('-b', mask, chan)

  def voice(self, mask, chan):
    """
    Give mask @mask voice on channel @chan.
    """
    self.mode('+v', mask, chan)

  def devoice(self, mask, chan):
    """
    Take voice from @mask on channel @chan.
    """
    self.mode('-v', mask, chan)

  def op(self, mask, chan):
    """
    Give mask @mask OP status on channel @chan.
    """
    self.mode('+o', mask, chan)

  def deop(self, mask, chan):
    """
    Take OP status from mask @mask on channel @chan.
    """
    self.mode('-o', mask, chan)

  def kick(self, chan, nicks=[], reason=None):
    """
    Kick nick(s) @nicks from channel @chan for reason @reason.
    """
    if not nicks:
      return

    if reason is None:
      r = ''
    else:
      r = " :%s" % reason
    self._send("KICK %s %s%s" % (chan, ','.join(nicks), r))

  def join(self, chan):
    """
    Join channel @chan.
    """
    self._send("JOIN %s" % chan)
    self.channels.add(chan)
    self.handler.handle_join(chan)

  def leave(self, msg, chan):
    """
    Leave channel @chan with reason @msg.
    """
    self._send("PART %s :%s" % (chan, msg))
    if chan in self.channels:
      self.channels.remove(chan)

  def quit(self, msg=None):
    self.connected = False
    if msg:
      self._send("QUIT :%s" % msg)
    else:
      self._send("QUIT")

  #### Internals ####
  def _send(self, msg):
    """
    Send something (anything) to the IRC server.
    """
    print "Sending: %s\r\n" % msg
    self.sock.send(("%s\r\n" % msg).encode('utf-8'))

  def pong(self, trail):
    self._send("PONG %s" % trail)

  def receive(self):
    """
    Read from the socket until we reach the end of an IRC message.
    Attempt to decode the message and return it.
    Call handle_encoding_error() if unsuccessful.
    """
    buf = []
    while True:
      nxt_ch = None
      ch = self.sock.recv(1)
      if ch == b'\r':
        nxt_ch = self.sock.recv(1)
        if nxt_ch == b'\n':
          try:
            line = b''.join(buf).decode('utf-8')
          except(UnicodeEncodeError, UnicodeDecodeError):
            self.handle_encoding_error()
            return ''
          print "received: %s" % line
          return line
      buf.append(ch)
      if nxt_ch:
        buf.append(nxt_ch)
    if not line.strip():
      return None
    else:
      try:
        parsable = line.strip(b'\r\n').decode('utf-8')
        print "Received: %s" % parsable
        return parsable
      except(UnicodeEncodeError, UnicodeDecodeError):
        self.handle_encoding_error()

  def parse(self, line):
    if not line:
      # empty line; this should throw up an error
      return
    line = line.strip('\r\n')
    tokens = line.split(' ')
    if tokens[0].startswith(':'):
      prefix = tokens.pop(0)[1:].strip(':')
    else:
      prefix = ''
    # Apparently, mIRC does not send uppercase commands (from Twisted's IRC)
    cmd = tokens.pop(0).upper()
    if cmd == '433':      # nick already in use
      self.nick += '_'
      self._send("NICK %s" % self.nick)
    elif cmd == '376':    # end of MOTD
      self.on_connect()
    elif cmd == '422':    # No MOTD file
      self.on_connect()
    elif cmd == '353':    # Names list
      self.handler.handle_name_list(tokens)
    elif cmd == 'PING':
      self.pong(' '.join(tokens))
    elif cmd == 'ERROR':
      self.handle_error(tokens)
    elif cmd == 'KICK':
      self.handler.handle_kick(tokens, prefix)
    elif cmd == 'JOIN':
      if prefix.split('!')[0] != self.nick:
        self.handler.handle_other_join(tokens, prefix)
    elif cmd == 'PRIVMSG':
      self.handler.handle_privmsg(tokens, prefix)

  def handle_encoding_error(self):
    print 'Encoding error encountered.'

  def handle_error(self, tokens):
    print "Error. tokens: %s" % tokens
    if tokens[0] == ':Closing' and tokens[1] == 'Link:':
      if tokens[3] == '(Ping' and tokens[4] == 'timeout:':
        time.sleep(5)
        self.connect()
      else:
        sys.exit(1)

  def on_connect(self):
    """
    Called once we have connected to and identified with the server.
    Mainly joins the channels that we want to join at the start.
    """
    for chan in self.join_first:
      self.join(chan)

class Bot(object):
  """
  The bot class. This will create the IRCConn object and handle it.
  For now I plan to just use the global variables @com and @ident but
  I should really make this more like a class eventually.
  """
  def __init__(self, ident):
    self.ident = ident
#    self.cmds = com
    self.conn = IRCConn(self)
    self.conn.connect()

  def handle_privmsg(self, tokens, sender):
    chan = tokens.pop(0)
    tokens[0] = tokens[0].strip(':')
    if tokens[0] == self.ident['nick']:
      l = [tokens.pop(0)]
      is_to_me = True
    else:
      is_to_me = False
    nick, host = sender.split('!')
    if chan == self.ident['nick']:
      chan = nick
    data = {'channel': chan, 'sender': sender, 'is_to_me': is_to_me,
            'nick': nick, 'host': host}
    cmd = tokens[0]
    try:
      args = tokens[1:]
    except IndexError:
      args = []
    if is_to_me and cmd == 'reload':
      if data['sender'] == com.trusted:
        reload(com)
        self.conn.say('Commands module reloaded', data['sender'].split('!')[0])
      else:
        self.conn.say('┌∩┐(ಠ_ಠ)┌∩┐'.decode('utf-8'), data['sender'].split('!')[0])
    elif is_to_me:
      com.AddrFuncs(cmd, args, data, self.conn)
    else:
      com.UnAddrFuncs(cmd, args, data, self.conn)

  def handle_name_list(self, tokens):
    tokens.pop(0) # get rid of our nick from the beginning of the msg.
    tokens.pop(0) # get rid of the equals sign
    chan = tokens.pop(0)
    try:
      self.conn.nicks[chan] += [t.lstrip(':') for t in tokens]
    except:
      self.conn.nicks[chan] = [t.lstrip(':') for t in tokens]

  def handle_join(self, channel):
    com.OnJoinFuncs(channel, self.conn)

  def handle_other_join(self, tokens, joiner):
    chan = tokens.pop().strip(':')
    nick, host = joiner.split('!')
    data = {'channel': chan, 'joiner': joiner, 'nick': nick, 'host': host}
    com.OtherJoinFuncs(data, self.conn)

  def handle_kick(self, tokens, sender):
    chan = tokens.pop(0)
    tokens[0] = tokens[0].strip(':')
    if tokens[0] == self.ident['nick']:
      tokens.pop(0)
      is_about_me = True
    else:
      is_about_me = False
    nick, host = sender.split('!')
    data = {'channel': chan, 'sender': sender, 'nick': nick, 'host': host, 'kickee': tokens.pop(0)}
    msg = tokens[0].lstrip(':') if tokens else None
    if is_about_me:
      com.OnKickedFuncs(msg, data, self.conn)
    else:
      com.OtherKickedFuncs(msg, data, self.conn)

  def main(self):
    """
    Run the mainloop.
    """
    self.conn.mainloop()

potbot = Bot(freenode)
#potbot = Bot(efnet)
