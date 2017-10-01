from channels import Group
from channels.sessions import channel_session
import random
from .models import Player, Group as OtreeGroup, Constants
import json
import time


def ws_connect(message, group_name):
    Group(group_name).add(message.reply_channel)



# Connected to websocket.receive
def ws_message(message, group_name):
    group_id = group_name[5:]
    print('GROUP ID', group_id)
    print('PLAYER::::', message['text'])
    jsonmessage = json.loads(message.content['text'])
    mygroup = OtreeGroup.objects.get(id=group_id)
    curbuyer_id = jsonmessage['id']
    curbuyer_id_in_group = jsonmessage['id_in_group']
    mygroup.price += 10

    mygroup.buyer = curbuyer_id_in_group
    now = time.time()
    mygroup.auctionenddate = now + Constants.extra_time

    session = mygroup.session
    print ('curbuyer id --> ', curbuyer_id, type(curbuyer_id))
    session.vars['offers'][str(curbuyer_id)] += 1

    player = mygroup.get_player_by_id(curbuyer_id_in_group)
    player.offers += 1

    mygroup.save()
    player.save()
    session.save()
    time_left = round(mygroup.auctionenddate - now)
    textforgroup = json.dumps({
                                "dicc_offers": session.vars['offers'],
                                "price": mygroup.price,
                                "newauctionendtime": mygroup.auctionenddate,
                                "time_left": time_left,
                                "winner": curbuyer_id_in_group,
                                })

    groups = mygroup.get_id_groups()

    # send to all the groups,because need update the information for other player in the session
    for g in groups:
        name = 'group'+str(g.id)
        Group(name).send({
                        "text": textforgroup
                        })





# Connected to websocket.disconnect
def ws_disconnect(message, group_name):
    Group(group_name).discard(message.reply_channel)
