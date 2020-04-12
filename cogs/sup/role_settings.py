"""
Settings

Name: string, only required argument.
Colour: hex code or string (only common names are defined)
Position: int or string (name of role to be placed under)
Hoist: bool, (show the role separately in member list)
Mentionable:  bool, (this is a good way to annoy people)

Permisions

Some permissions are global (i.e. ban) while others are channel
specific. The default value for all global permissions is False.
Channel specific permissions can overwrite global permissions,
and their default value is None, meaning unchanged.


 1 create_instant_invite 00000001 T, V
 2 kick_members          00000002 *,
 3 ban_members           00000004 *,
 4 administrator         00000008 *,
 5 manage_channels       00000010 *, T, V
 6 manage_guild          00000020 *,
 7 add_reactions         00000040 T
 8 view_audit_log        00000080
 9 view_channel          00000400 T, V
10 send_messages         00000800 T
11 send_tts_messages     00001000 T
12 manage_messages       00002000 *, T
13 embed_links           00004000 T
14 attach_files          00008000 T
15 read_message_history  00010000 T
16 mention_everyone      00020000 T
17 use_external_emojis   00040000 T
18 view_guild_insights   00080000
19 connect               00100000 V
20 speak                 00200000 V
21 mute_members          00400000 V
22 deafen_members        00800000 V
23 move_members          01000000 V
24 use_vad               02000000 V
25 priority_speaker      00000100 V
26 stream                00000200 V
27 change_nickname       04000000
28 manage_nicknames      08000000
29 manage_roles          10000000 *, T, V
30 manage_webhooks       20000000 *, T, V
31 manage_emojis         40000000 *,
"""
