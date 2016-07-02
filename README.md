# SpaceCake

This is a python IRC bot created by hacking on pydsigner's project here: https://github.com/pydsigner/IRC

In order to use you'll need a module named ident.py with dictionaries (profiles), one per server.
The 'chan' key is expected to be a table of channel names.

There is a template included in the ident.py file in this repo.

Ex:
server1 = {
  'ident': ,
  'host': ,
  'port': ,
  'nick': ,
  'real_name': ,
  'chan': [],
  'trusted':
}
