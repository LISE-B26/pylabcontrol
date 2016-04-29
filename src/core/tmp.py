from src.instruments import MaestroLightControl
from src.core import Instrument



instr, fail = Instrument.load_and_append({'MaestroLightControl': {'class': 'MaestroLightControl', 'settings': {'port': 'COM5', 'block green': {'settle_time': 0.2, 'position_open': 7600, 'position_closed': 3800, 'open': True, 'channel': 0}}}})
print(instr)
# light = MaestroLightControl()
# # print(light.settings)
# light.update({'block green': {'open': False}})
# # light.settings.update({'block green': {'open': True}})
# print(light.Mins)