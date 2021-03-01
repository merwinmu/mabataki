from websocket import create_connection
import json
import random
import string
import re
import csv
import numpy as np
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import data, wb
from Plotter import getValue
from Plotter import getClose
from Plotter import getSenkouA
from Plotter import getSenkouB

import threading
import schedule
import time
import datetime as dt
import smtplib, ssl

class ThreadWithResult(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, *, daemon=None):
        def function():
            self.result = target(*args, **kwargs)
        super().__init__(group=group, target=function, name=name, daemon=daemon)

values = []
threads = []


def filter_raw_message(text):
    try:
        found = re.search('"m":"(.+?)",', text).group(1)
        found2 = re.search('"p":(.+?"}"])}', text).group(1)
    #    print(found)
    #    print(found2)
        return found1, found2
    except AttributeError:
        print("error")
    

def generateSession():
    stringLength=12
    letters = string.ascii_lowercase
    random_string= ''.join(random.choice(letters) for i in range(stringLength))
    return "qs_" +random_string

def generateChartSession():
    stringLength=12
    letters = string.ascii_lowercase
    random_string= ''.join(random.choice(letters) for i in range(stringLength))
    return "cs_" +random_string

def prependHeader(st):
    return "~m~" + str(len(st)) + "~m~" + st

def constructMessage(func, paramList):
    #json_mylist = json.dumps(mylist, separators=(',', ':'))
    return json.dumps({
        "m":func,
        "p":paramList
        }, separators=(',', ':'))

def createMessage(func, paramList):
    return prependHeader(constructMessage(func, paramList))

def sendRawMessage(ws, message):
    ws.send(prependHeader(message))

def sendMessage(ws, func, args):
    ws.send(createMessage(func, args))

def generate_csv(a,id):
    out= re.search('"s":\[(.+?)\}\]', a).group(1)
    x=out.split(',{\"')
    
    with open(id+'.csv', mode='w', newline='') as data_file:
        employee_writer = csv.writer(data_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    
        employee_writer.writerow(['index', 'date', 'open', 'high', 'low', 'close', 'volume'])
        
        for xi in x:
            xi= re.split('\[|:|,|\]', xi)
           # print(xi)
            ind= int(xi[1])
            ts= datetime.fromtimestamp(float(xi[4])).strftime("%Y/%m/%d, %H:%M:%S")
            employee_writer.writerow([ind, ts, float(xi[5]), float(xi[6]), float(xi[7]), float(xi[8]), float(xi[9])])

def schedule_actions():
    
  # Every Monday task() is called at 20:
  # TODO CHANGE TO 9

  schedule.every(1).minutes.do(start_thread)
  signal_list = start_thread()
  # Checks whether a scheduled task is pending to run or no
  while True:
    schedule.run_pending()
    time.sleep(1)            


def send_mail(text):
    port = 587  # For starttls
    smtp_server = "smtp.gmail.com"
    sender_email = "ichimokupython@gmail.com"
    receiver_email = "p.panthalattiyil@gmail.com"
    password = "ichimoku123"
    message = """\
    Subject: Ichimoku Sensei

    This message is sent from Python 
    

    """ + text 


    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)


def job_function(id):

    if dt.datetime.today().weekday() != 6:
        # Initialize the headers needed for the websocket connection
        headers = json.dumps({
            # 'Connection': 'upgrade',
            # 'Host': 'data.tradingview.com',
            'Origin': 'https://data.tradingview.com'
            # 'Cache-Control': 'no-cache',
            # 'Upgrade': 'websocket',
            # 'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
            # 'Sec-WebSocket-Key': '2C08Ri6FwFQw2p4198F/TA==',
            # 'Sec-WebSocket-Version': '13',
            # 'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.56',
            # 'Pragma': 'no-cache',
            # 'Upgrade': 'websocket'
        })

        print("schedule job started")

        interval = 1
        values = []

        # TODO CHANGE TO 16

        while( 2 >= interval):                    
            val = interval * 15

            print("Value at " + str(val))
            # Then create a connection to the tunnel
            ws = create_connection(
                'wss://data.tradingview.com/socket.io/websocket',headers=headers)

            session= generateSession()
    #     print("session generated {}".format(session))

            chart_session= generateChartSession()
    #     print("chart_session generated {}".format(chart_session))


            # Then send a message through the tunnel 
            sendMessage(ws, "set_auth_token", ["unauthorized_user_token"])
            sendMessage(ws, "chart_create_session", [chart_session, ""])
            sendMessage(ws, "quote_create_session", [session])
            sendMessage(ws,"quote_set_fields", [session,"ch","chp","current_session","description","local_description","language","exchange","fractional","is_tradable","lp","lp_time","minmov","minmove2","original_name","pricescale","pro_name","short_name","type","update_mode","volume","currency_code","rchp","rtc"])
            sendMessage(ws, "quote_add_symbols",[session, id, {"flags":['force_permission']}])
            sendMessage(ws, "quote_fast_symbols", [session,id])

            #st='~m~140~m~{"m":"resolve_symbol","p":}'
            #p1, p2 = filter_raw_message(st)
            sendMessage(ws, "resolve_symbol", [chart_session,"symbol_1","={\"symbol\":\""+id+"\",\"adjustment\":\"splits\",\"session\":\"extended\"}"])
            sendMessage(ws, "create_series", [chart_session, "s1", "s1", "symbol_1", str(val), 2000])
            #sendMessage(ws, "create_study", [chart_session,"st4","st1","s1","ESD@tv-scripting-101!",{"text":"BNEhyMp2zcJFvntl+CdKjA==_DkJH8pNTUOoUT2BnMT6NHSuLIuKni9D9SDMm1UOm/vLtzAhPVypsvWlzDDenSfeyoFHLhX7G61HDlNHwqt/czTEwncKBDNi1b3fj26V54CkMKtrI21tXW7OQD/OSYxxd6SzPtFwiCVAoPbF2Y1lBIg/YE9nGDkr6jeDdPwF0d2bC+yN8lhBm03WYMOyrr6wFST+P/38BoSeZvMXI1Xfw84rnntV9+MDVxV8L19OE/0K/NBRvYpxgWMGCqH79/sHMrCsF6uOpIIgF8bEVQFGBKDSxbNa0nc+npqK5vPdHwvQuy5XuMnGIqsjR4sIMml2lJGi/XqzfU/L9Wj9xfuNNB2ty5PhxgzWiJU1Z1JTzsDsth2PyP29q8a91MQrmpZ9GwHnJdLjbzUv3vbOm9R4/u9K2lwhcBrqrLsj/VfVWMSBP","pineId":"TV_SPLITS","pineVersion":"8.0"}])


            # Printing all the result
            a=""
            i = 0
            while i  < 10:
                try:
                    result = ws.recv()
        #            print(result)
                    a=a+result+"\n"
                    i=i+1
                except Exception as e:
                    print(e)
                    break
                
            generate_csv(a,id)

            values = np.append(values,getValue(id))

            interval = interval + 1

            if interval == 5:
                interval = 16

            if interval == 3:
                interval = 4

        print(values)

        check = all(x==values[0] for x in values)

        check_false = True

        print("schedule job finished "+id)


        if check:
            check_false = True
            if values[0] == 1:
                result_signal = ["Buy", id, "Close Price: "+ str(getClose()), "Senkou A "+ str(getSenkouA()), "Senkou B "+ str(getSenkouB())]
                return result_signal
            else:
                result_signal = ["Sell", id,"Close Price: "+ str(getClose()), "Senkou A "+ str(getSenkouA()), "Senkou B "+ str(getSenkouB())]
                return result_signal
        else:
            print("Elements are not equal")

currency_list = ["FOREXCOM:EURUSD","FOREXCOM:USDCHF","FOREXCOM:EURCHF","FOREXCOM:CADCHF","FOREXCOM:EURGBP","FOREXCOM:EURCAD"]
thread_list = []
def start_thread():
    print("Thread started")


    for x in range (len(currency_list)):
        thread = ThreadWithResult(target=job_function, args=(currency_list[x],))
        thread_list.append(thread)
        thread.start()

    message = ""        
    for x in range(len(thread_list)):
        thread_list[x].join()

    for x in range(len(thread_list)):
        message+=(str(thread_list[x].result) + " \n\n")

#     thread1.start()
#     thread2.start()
#     thread3.start()
#     thread4.start()
#     thread5.start()
#    # thread6.start()
#    # thread7.start()
#    # thread8.start()
    
#     thread1.join()
#     thread2.join()
#     thread3.join()
#     thread4.join()
#     thread5.join()
#    # thread6.join()
#    # thread7.join()
#    # thread8.join()

#   message = str(thread1.result) + " \n\n" + str(thread2.result) + " \n\n" + str(thread3.result)  + " \n\n" +   str(thread4.result)+ " \n\n" + str(thread5.result) 
    send_mail(message)

    print(message)

    message = ""
    thread_list.clear()



schedule_actions()