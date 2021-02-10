# Grid strategy robot for crypto trading in Robinhood
A.) Abstract: Implement the grid strategy for crypto trading in Robinhood. This robot helps you with a robust and low-risk straegy to invest. However, the lower bound & upper bound have to set up carefully to find the balance between the profit and the risk. One can see the strategy detail from https://www.valutrades.com/en/blog/how-to-trade-currency-using-a-grid-strategy , which gives a concrete example and nice explanation. 
 
B.) Instruction:
 run "RH_main.py" to start the robot. Edit "config.yaml" to setup your configuration. The essential python packages are "robin_stocks", "playsound". IMPORTANT!!! the current robot is semi-automatic since it only places the buy/ sell orders into Robinhood at appropriate timings but will not track the orders which are being taken or not. Use with caution.
 
C.) Parameter setting for "config.yaml":
 
 invest: #parameters mainly for the investment
  
  sym: The symbol of the crypto you want to trade ("E.g., BTC")
  
  budget: The total amount of your investment
  
  lb: The lower bound of your grids
  
  up: The upper bound of your grids
  
  n_intervals: The number of grids between your upper bound and lower bound
  
  user_name: Your user name in robinhood (can setup as "" and type later)
  
  user_pd: Your password in robinhood (can setup as "" and type later)
  
  store_login_token: Either save your login information (token) or not
  
  token_expire_time: The expiration time of your saved token (unit as minute)

exec: #parameters for execution trades
  
  fake_open_position: Either open a fake position or not. E.g., set it as True if you already have a position.
  
  fake_action: Fake the buy/ sell actions. set it as True for testing.
  
  open_position_price: Open the position if the price is lower than this value (Can set up as None)

prog: #parameters for the robot setting
  
  qrange_min: Randomized query time range (at least), unit as minute 
  
  qrange_max: Randomized query time range (at most), unit as minute 
  
  info_level: ("debug" or "info" or "simple") Levels of the detail in printed information: debug> info> simple
 
 
