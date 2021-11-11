### plot location of iss, location data from API json
###made on 1 nov 2021

import pandas as pd
import plotly.express as px

url = 'http://api.open-notify.org/iss-now.json'
dfr = pd.read_json(url)
dfr['latitude'] = dfr.loc['latitude','iss_position']
dfr['longitude'] = dfr.loc['longitude','iss_position']
dfr.reset_index(inplace=True)
dfr = dfr.drop(['index','message'], axis=1)
plt = px.scatter_geo(dfr,lat='latitude',lon='longitude')
plt.show()