from datetime import datetime,timedelta
#program needed
import robin_stocks as r
import numpy as np
import random as rn
from collections import OrderedDict 
from playsound import playsound

#login
import logging as lg
import argparse
import yaml
import os

def parse_args():
  """Parse command line arguments."""
  hpo_warning = 'Flag overwrites config value if set, used for HPO and PBT runs primarily'
  parser = argparse.ArgumentParser('RH_main.py')
  add_arg = parser.add_argument
  add_arg('config', nargs='?', default='config.yaml')
  return parser.parse_args()


def find_index_at_most(array, value):
    array = np.asarray(array)
    idx = list((array - value)>0).index(True)
    if idx==0:
      raise ValueError
    return idx-1

    
def exec_tran(als,v,lv,cns,op,fk=False):
  if als[v]=="none":
    return [als,op,"none"]
  
  elif als[v]=="b":
    if fk==False:
      info=r.orders.order_buy_crypto_limit(sym,cns,round(v,6))
      lg.info("Buy info: ",info)
      print("### I buy at ",round(v,6), " Buy and HOLD! # ",op)
    else:
      print("### I faked buy at ",round(v,6), " Buy and HOLD! # ",op)
    
    als[v]="none"
    als[v+lv]="s"
    return [als,op+1,"b"]
  
  elif als[v]=="s":
    if fk==False:
      info=r.orders.order_sell_crypto_limit(sym,cns,round(v,6))
      lg.info("Sell info: ",info)
      print("### I sell at ",round(v,6), " Hands shaking # ",op)
    else:
      print("### I faked sell at ",round(v,6), " Hands shaking # ",op)
    
    als[v]="none"
    als[v-lv]="b"
    return [als,op+1,"s"]
  else:
    lg.ERROR("### Invalid ACTION: %s",als[v])
    return [None,None,None]

def load_config(config_file, output_dir=None, **kwargs):
  with open(config_file) as f:
      config = yaml.load(f, Loader=yaml.FullLoader)
  # Update config from command line, and expand paths
  for key, val in kwargs.items():
      config[key] = val
  return config

def set_info_level(var):
  if var=="debug":
    lg.basicConfig(level=lg.DEBUG)
  if var=="info":
    lg.basicConfig(level=lg.INFO)
  return
  
def main():
  #load config
  args = parse_args()
  config=load_config(args.config)
  set_info_level(config['prog']['info_level'])
  lg.basicConfig(level=lg.INFO)
  lg.info("### The input configuration: %s",config)
  
  #login
  d=config['invest']
  sym,n_intervals, up, lb,budget=d['sym'],d['n_intervals'],d['up'],d['lb'],d['budget']
  login = r.login(d['user_name'],d['user_pd'],store_session=d['store_login_token'],expiresIn=d['token_expire_time']*60)
  lg.info("### Crpto information: %s",r.crypto.get_crypto_quote(sym))
  y=r.crypto.get_crypto_positions(info=None)[0]
  cuq=float(y['quantity'])
  if cuq>0:
    lg.warning("### Right now you are holding: %s coins, with helding for buy: %s and helding for sell: %s", y['quantity'],y['quantity_held_for_buy'],y['quantity_held_for_sell'])
  
  #setup grid positions
  if n_intervals is not None:
    iv=(up-lb)/n_intervals #grid width by coin price
    iv=round(iv,6) #round in 6 demicials
    mny=budget/n_intervals #money for each grid
  x=lb
  earning = 0
  tp=[]
  while x<up:
    tp.append(x)
    x+=iv
  print("==========================================================================")
  print("My grids: ",tp, "average grid width: ",mny," pnt:",2*iv/(up+lb)*100, "%")
  print("==========================================================================")
  als=OrderedDict() #action list
  
  #price threshold to open the position
  qg=[float(config['prog']['qrange_min']),float(config['prog']['qrange_max'])]
  opp,fk_open,fk_action=config['exec']['open_position_price'],config['exec']['fake_open_position'],config['exec']['fake_action']
  qtime=-1
  qtm=rn.uniform(qg[0], qg[1])
  if opp is not None:
    while True:
      now= datetime.now()
      if qtime==-1 or now>qtime+timedelta(minutes = qtm): #report time
        qtm=rn.uniform(qg[0], qg[1])
        cv=float(r.crypto.get_crypto_quote(sym)["mark_price"])
        cv=round(cv,6)
        if cv<=opp:
          break
        print("Time: ",now, "price: ",cv," Patient, this is not the right time. Remember your promise, price: ",opp)
        qtime=now
  
  #open initial position
  cv=float(r.crypto.get_crypto_quote(sym)["mark_price"])
  cv=round(cv,6)
  try:
    gid=find_index_at_most(tp,cv)
    cash=gid*mny
    inve=budget-cash
    print("==========================================================================")
    if fk_open==True:
      print("Position ready to faked open!!")
    else:
      print("Position ready to open!!")
    print("Current Price: ",cv," Your cash:", cash, " Invested:",inve)
    print("==========================================================================")
    inp = input("Are you sure you want to continue? (type 'n' to leave):  ")
    if inp=="n":
      return
    if not fk_open:
      info=r.orders.order_buy_crypto_limit(sym,inve//cv,cv)
      lg.info("Buy info: %s",info)
    
    #SET BUY PRICE
    for i in range(0,gid):
      als[tp[i]]="b"
    #SET current pos as nothing to do
    als[tp[gid]]="none"
    #SET SELL PRICE
    for i in range(gid+1,len(tp)):
      als[tp[i]]="s"
    print("Action list: ",als.items())
  except:
    print("ERROR: the market price is ",cv, ". Outside the grids.")
    return

  #real-time checking price and moving grid
  op=0
  qtm=rn.uniform(qg[0], qg[1])
  ptime = datetime.now()
  qtime = datetime.now()
  while True:
    now= datetime.now()
    if now>qtime+timedelta(minutes = 1): #report time
      print("Time: ",now," Last query price: ",cv, " Bid price (you can sell with): ", bprice, " Ask price (you can buy with): ", aprice)
      qtime=now
    
    if now > ptime + timedelta(minutes = qtm): #for every minute
      ptime=now
      qtm=rn.uniform(qg[0], qg[1])
      info=r.crypto.get_crypto_quote(sym)
      cv=round(float(info["mark_price"]),6)
      bprice=round(float(info["bid_price"]),6)
      aprice=round(float(info["ask_price"]),6)

      try:
        ngid=find_index_at_most(tp,cv)
      except: #out of grids case
        lg.warning("#### The market price is ",cv, ". Outside the grids.")
        info=r.crypto.get_crypto_positions(info=None)[0]
        cns=info['quantity_available']
        info=r.orders.order_sell_crypto_limit(sym,cns,round(cv,6))
        lg.info("Sell info: ",info)
        print("### I sell at ",round(cv,6), "with quantity",cns)
        if cv<lb:
          print("Are you winning, son?")
        else:
          print("Breaks the top!")
          playsound('dat/victory.mp3')
        return
      if gid<ngid: #sell and put a buy
        for i in range(gid+1,ngid+1):
          als,op,a=exec_tran(als,tp[i],iv,mny//cv,op,fk_action)
          if a=="s":
            lg.info("Action list: ",als.items())
            earning+=iv*(mny//cv)
            print("Current earning: ",earning)
      elif gid>ngid: #buy and put a sell
        for i in range(gid,ngid,-1):
          als,op,a=exec_tran(als,tp[i],iv,mny//cv,op,fk_action)
          if a=="b":
            lg.info("Action list: ",als.items())
      gid=ngid
      
    
if __name__ == '__main__':
  main()