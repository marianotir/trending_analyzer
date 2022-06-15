
#-----------------
# Modules
#----------------

import csv
import pandas as pd
import datetime as dt
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
from telethon.tl.types import PeerChannel
from telethon.sync import TelegramClient
from telethon import TelegramClient
from telethon.tl.types import InputPeerChat
import re
from re import search
import os
import config
import requests
import time
import sys


# ----------------------
# Define Functions 
# ----------------------

# Define connection
def connect_tg():

    client = TelegramClient(config.phone, config.api_id, config.api_hash)

    return client


def send_message(value):

    time.sleep(5)

    api_messages = config.api_messages
    chat_id_messages = config.chat_id

    channel_api = 'bot'+ api_messages
    chat_id = chat_id_messages

    url = 'https://api.telegram.org/'+channel_api+'/sendMessage?chat_id=-'+chat_id+'&text="{}"'.format(value)
    requests.get(url)


def test_connection():
        text = 'Testing connection'
        print(text)
        send_message(text)


def get_chat_message(client,chat) -> object:

    with client:
        for msg in client.iter_messages(chat, 1):
           message_text = msg.text

    return message_text


def get_trending(message):

    col_names = ['position','token']
    data  = pd.DataFrame(columns = col_names)
    df_temp  = pd.DataFrame(columns = col_names)

    trending = ['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15']
    for i in trending:
        start = message.find('*' + i)
        end = message.find('** [', start)
        token = message[start:end]
        token = token.replace("*","")
        token = token.split(" ", 1)[1].rsplit(" ", 1)[0]

        df_temp.loc[0,'position'] = int(i)
        df_temp.loc[0,'token'] = token

        data = pd.concat([data, df_temp], ignore_index=True)

        print(i+':'+token)

    return data


def update_position(token_hist_list,token,new_position):

    token_hist_list.loc[token_hist_list['token']==token,'position'] = new_position

    return token_hist_list


def add_token(data_token_hist_list,token,position,chain):

    df_temp = pd.DataFrame([[token,position,chain]], columns = ['token','position','chain'])

    token_hist_list = pd.concat([data_token_hist_list, df_temp], ignore_index=True)

    return token_hist_list


def check_token(token_trending_list,token_hist_list,chain):

    for token in token_trending_list.token.unique():

        token_pos = token_trending_list[token_trending_list['token']==token].position.values[0]

        if token in token_hist_list.token.unique():

            token_old_pos = token_hist_list[token_hist_list['token']==token].position.values[0]

            if token_pos == token_old_pos:
                pass
            else:

                if token_pos < token_old_pos:
                    message_info = '****** \n Trending UP: ++ ' + token + '\n    from: ' + str(token_old_pos) + '\n    to: ' + str(token_pos) +'\n ****** \n'
                else:
                    message_info = '****** \n Trending DOWN: -- ' + token + '\n   from: ' + str(token_old_pos) + '\n   to: ' + str(token_pos) +'\n ****** \n'

            # update position
            token_hist_list = update_position(token_hist_list,token,token_pos)

        else:

            message_info = 'A new token is trending!! in ' + chain + ' chain: '  '\n' + token + '\n in position: ' + str(token_pos) +'\n'

            # add to token list
            token_hist_list = add_token(token_hist_list,token,token_pos,chain)

            send_message(message_info)
            print('****** \n')
            print(message_info)
            print('****** \n')
            print('\n')

    return token_hist_list


def update_token_hist(token_hist_list,data_trending_list):

    for token in token_hist_list.token.unique():
        if token not in data_trending_list.token.unique():
            new_position = 100
            token_hist_list = update_position(token_hist_list,token,new_position)

    return token_hist_list


def get_init_token_list(data_trending_list,chain):

    columns_hist =['token','position','chain']
    data_trending_list['chain'] = chain
    token_hist_list = data_trending_list[columns_hist]

    return token_hist_list


def get_tg_channel(chain):

    if chain in config.chain_list:
        print('Network selected: ' + chain)

    else:
        print('Network does not exist')
        exit()

    return chain


# ----------------------
# Main Function 
# ----------------------

def main(network):

    print('Initiate Connection... \n')

    client = connect_tg()
    client.connect()

    tg_chain = get_tg_channel(network)

    print('Send Connection message... \n')
    send_message('********************* \n Initial Connection to network: ' + network + '\n *********************')

    print('Get init trending list... \n')
    message = get_chat_message(client,tg_chain)
    df_list_init = get_trending(message)
    token_hist_list = get_init_token_list(df_list_init,network)

    time.sleep(10)

    text = 'Trending Screening Begins'
    print(text)
    send_message(text)

    time.sleep(120)

    print('Begin tracking trending... \n')
    
    num = 0
    while True:

        print('Checking trending... \n')

        message = get_chat_message(client,tg_chain)

        df_trending = get_trending(message)

        token_hist_list = check_token(df_trending,token_hist_list,network)

        token_hist_list = update_token_hist(token_hist_list,df_trending)

        num+=1 
        if num == 500:
            num = 0
            test_connection()

        time.sleep(120)


if __name__ == "__main__":
    main(sys.argv[1])
