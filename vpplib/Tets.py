import environment
Environment=environment.Environment(start='2015-01-01 00:00:00',end='2015-12-31 00:00:00')
Environment.get_dwd_pv_data(lat=50.0,lon=8.0)