import pandas as pd
import pvlib
from pvlib import pvsystem
from pvlib.pvsystem import PVSystem
from pvlib.location import Location
from pvlib.modelchain import ModelChain
import matplotlib.pyplot as plt
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS



sandia_modules = pvsystem.retrieve_sam(name='SandiaMod')
inverters = pvsystem.retrieve_sam('sandiainverter')
temperature_model_parameters = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

inverter = inverters['ABB__PVI_3_0_OUTD_S_US__208V_']
module = sandia_modules['Canadian_Solar_CS5P_220M___2009_']

mps=5
spi=2



parameters = {
    'Name': 'Canadian Solar CS5P-220M',
    'BIPV': 'N',
    'Date': '10/5/2009',
    'T_NOCT': 42.4,
    'A_c': 1.7,
    'N_s': 96,
    'I_sc_ref': 5.1,
    'V_oc_ref': 59.4,
    'I_mp_ref': 4.69,
    'V_mp_ref': 46.9,
    'alpha_sc': 0.004539,
    'beta_oc': -0.22216,
    'a_ref': 2.6373,
    'I_L_ref': 5.114,
    'I_o_ref': 8.196e-10,
    'R_s': 1.065,
    'R_sh_ref': 381.68,
    'Adjust': 8.7,
    'gamma_r': -0.476,
    'Version': 'MM106',
    'PTC': 200.1,
    'Technology': 'Mono-c-Si',
}



'''
surface_tilt= 30∞ roof pitch
surface_azimuth= 180∞ , direction south
modules per string: 
strings:
'''
system = PVSystem(surface_tilt=35, surface_azimuth=180,
                  module_parameters=module,
                  inverter_parameters=inverter,
                  temperature_model_parameters=temperature_model_parameters,
                  modules_per_string=mps,
                  strings_per_inverter=spi)

system.module_parameters = system.module_parameters.append(pd.Series(parameters))

#location: Euskirchen
location = Location(latitude=50.86677, longitude=7.14274)

weather = pd.read_csv('../weather_data/dwd_wind_data_2015.csv', sep=',', index_col=0, header=0,
                      date_parser=lambda idx: pd.to_datetime(idx, utc=True))
weather.head()


dc_model='cec'
mc = ModelChain(system, location, dc_model=dc_model)
mc.run_model(weather=weather)

mc.__dict__.keys()
#mc.ac.plot()
#plt.show()


dfpv = mc.ac.to_frame()
dfpv = dfpv.rename(columns={0: '1 Wp'})
dfpv['1 Wp'] = dfpv['1 Wp']/2200
dfpv['PV [W]'] = (dfpv['1 Wp'] * 1000000).astype(int)

dfpv.drop('1 Wp', axis=1, inplace=True)

#df['residential'] = df.iloc[:,1:3].sum(axis=1)
#df['agriculture'] = df['P [kW]'] * ((8*2))

#df['Gen_1_1'] = df['Gen_1_1'].astype(int)
#max_p = df.loc[df['Gen_1_1'].idxmax()]
#annual_production = df).sum()

#print(max_p)

#print(annual_production)
print(dfpv)
dfpv.plot(y=['PV [W]'], kind='line')
plt.show()

#dfpv.to_csv('pv_energy_cologne.csv')