# SpaceCake

This is a python IRC bot created by hacking on pydsigner's project here: https://github.com/pydsigner/IRC

In order to use you'll need a module named ident.py with dictionaries, one per server. The 'chan' key is expected to be a table of channel names.

Ex:
server1 = {
  'ident': ,
  'host': ,
  'port': ,
  'nick': ,
  'real_name': ,
  'chan': []
}
