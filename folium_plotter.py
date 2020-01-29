import folium
from folium import Element, Html
from folium.plugins import MarkerCluster
import folium.plugins as fp
import altair as alt
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import altair as alt
import html
import shutil
import os
#alt.renderers.enable('notebook')


def plot_table(dbmain, dbdata , idcol = 'BoreID',depthcol = 'FromDepth', datacol = 'Description', endholecol = 'BoreDepth'):

    """ Plot dataframe data on folium
    dbmain: dataframe with coordinates (Latitude and Longitude)
    dbdata: dataframe with data (specified in depthcol and datacol)
    datacol: string or list of column names from dbdata to plot against depthcol
    """

    print('Basemap options can be found here:  https://leaflet-extras.github.io/leaflet-providers/preview/')
    print('Marker options can be found here: https://fontawesome.com')
    
    ###Open Street Map
    tiles = 'OpenStreetMap'
    attr = ''
    
    ###ESRI Sattelite
    #attr = ('&copy; <a href="http://www.esri.com/">Esri</a>, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community')
    #tiles = 'http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'

    ###ESRI World topo
    #tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}'
    #attr = ('Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ, TomTom, Intermap, iPC, USGS, FAO, NPS, NRCAN, GeoBase, Kadaster NL, Ordnance Survey, Esri Japan, METI, Esri China (Hong Kong), and the GIS User Community')

    ###GOOGLE hybrid (does not work until attribution is found)
    #tiles = 'http://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}'  #Google hybrid
    
    centro = [dbmain['Latitude'].mean(),dbmain['Longitude'].mean()]
    
    #map = folium.Map(location= centro,tiles = 'OpenStreetMap',zoom_start=12)
    map = folium.Map(location= centro,tiles = tiles,attr = attr,zoom_start=12,max_zoom=19)
    my_cluster = MarkerCluster(disableClusteringAtZoom=17).add_to(map)

    
    
    bores = list(dbdata[idcol].drop_duplicates())
    
    for i in range(len(bores)):
        
        if type(datacol) == list:
            lithodata = dbdata[dbdata[idcol]==bores[i]][[depthcol] + datacol].copy()
        else:
            lithodata = dbdata[dbdata[idcol]==bores[i]][[depthcol,datacol]].copy()
        #print(bores[i])
        #print(lithodata)
        if lithodata[depthcol]._is_mixed_type:
            lithodata = lithodata[lithodata[depthcol]!='None']
        if len(lithodata) > 0:
            lithodata[depthcol]=lithodata[depthcol].astype(float)
            lithodata = lithodata.sort_values(by=[depthcol]).reset_index(drop=True)
            endofhole = max(max(dbmain[dbmain[idcol]==bores[i]][endholecol]),max(lithodata[depthcol]))
            
            longitude1=float(dbmain[dbmain[idcol]==bores[i]]['Longitude'])
            latitude1=float(dbmain[dbmain[idcol]==bores[i]]['Latitude'])
            
            #popup=folium.Popup(html = Html(lithodata.to_html))
            popup=folium.Popup('<b>'+'Bore:  </b>'+str(bores[i])+'<b>'+'       EOH(m): </b>'+str(endofhole)[0:5]+\
			'<br><b>'+'Loc: </b>'+str(longitude1)+','+str(latitude1)+'<br>'+lithodata.iloc[0:25].to_html(index = False),\
			max_width=350,min_width=200)
            
            
            #folium.Marker(location=[latitude1,longitude1],popup=popup).add_to(map) 
            folium.Marker(location=[latitude1,longitude1],popup=popup,icon=folium.Icon(icon='info-sign',color='red')).add_to(my_cluster)
            if np.mod(i,100)==0: 
                print(i)
        
    map.save('tester2.html')    
    

def plot_timecharts(dbmain, dbdata , idcol = 'BoreID',datecol = 'date', ycol = 'result', max_depth = 30, endholecol = 'BoreDepth'):

	""" Plot timeseries charts on folium
		dbmain: dataframe with coordinates (Latitude and Longitude)
		dbdata: dataframe with timeseries data (specified in datecol, ycol)

		saves files in currnet directory
		html files in /images
		folium map in current directory as 'tester1.html'
	"""

	#make directory for storing html images - delete any existing
	if 'WMPtt18images' in os.listdir():
		shutil.rmtree('WMPtt18images')
	os.makedirs('WMPtt18images')

	centro = [dbmain['Latitude'].mean(),dbmain['Longitude'].mean()]
	map = folium.Map(location= centro,tiles = 'OpenStreetMap',zoom_start=12,max_zoom=19)
	my_cluster = MarkerCluster(disableClusteringAtZoom=17).add_to(map)
	
	bores = list(dbdata[idcol].drop_duplicates())

	for i in range(len(bores)):
		levdata = dbdata[dbdata[idcol]==bores[i]]
		datevals = np.array(levdata[datecol])[0::5]
		longitude1=float(dbmain[dbmain[idcol]==bores[i]]['Longitude'])
		latitude1=float(dbmain[dbmain[idcol]==bores[i]]['Latitude'])
		endofhole = max(dbmain[dbmain[idcol]==bores[i]][endholecol])


		#y axis range
		if max(levdata[ycol]) < max_depth:
			levdomain = [0,max_depth]
		else:
			levdomain = [0,max(levdata[ycol])]

		#Altair chart
		chart1 = alt.Chart(levdata).encode(alt.Y(ycol+':Q',sort='descending',scale=alt.Scale(domain=levdomain)),x=datecol+':T').properties(\
		title='Bore: '+str(bores[i])+'  - depth to gwl (m)',width=400)
		chart1 = (chart1.mark_point(color='red')\
		+ chart1.mark_line()).interactive(bind_y=False)
        
		chart1.save('WMPtt18images\\'+str(bores[i])+'.html')
        
		
		#HTML
		s1=\
		'<b>Bore: </b>'+str(bores[i])+\
		'<br><b>Depth to groundwater = </b>'+str(levdata.sort_values(datecol).iloc[-1][ycol])+' m'\
		'<br><b>Date: </b>'+str(levdata.sort_values(datecol).iloc[-1][datecol])+\
		'<br><b>Bore depth: </b>'+str(endofhole)+' m'+\
		'<br><b>Loc: </b>'+str(longitude1)+','+str(latitude1)+'<br>'
		if len(levdata)>1:  #plot chart if more than on reading - string to popup html file (from disk) to new window with specified size
			#htmlstring = """<a href="#" target="_blank" onClick="window.open('C:/Users/A_Orton/Desktop/python_codes/1_DEM_plotting_and_section/ARUP_version_testing/images/well"""+str(i)+""".html','pagename','resizable,height=400,width=520'); return false;">Groundwater plot</a>"""
			htmlstring = """<a href="#" target="_blank" onClick="window.open('WMPtt18images/"""+str(bores[i])+""".html','pagename','resizable,height=400,width=520'); return false;">Groundwater plot</a>"""
			h1=Html(s1+htmlstring.replace('\'','&#39'),script=True) #Critical to remove single quotes from the string by replacing \' with &#39
			popup=folium.Popup(h1,max_width=350,min_width=200)
		else:    #else display value only
			popup = folium.Popup(str(s1),max_width=350,min_width=200)
		folium.Marker(location=[latitude1,longitude1],popup=popup,icon=folium.Icon(icon='info-sign',color='blue')).add_to(my_cluster)              
		
		if np.mod(i,100)==0: 
			print(i)
       

	map.save('tester1.html')


    
if __name__=="__main__":

	import extract_from_SQLdatabase as extmain
	#import create_database_from_NGISdata as crt
	
	#INPUT
	plot_litho_tables = True
	plot_gwl_timeseries = True
	
	database_directory=r'C:\Users\Antony.Orton\Desktop\Python_programs\foliumwebmaptools' #directiory in which the .db files reside
	databasename='NSWBoreDatabase.db'

	extents = [151.131797,-33.440765,151.319761,-33.338318]


	#END OF INPUT
	
	
	print('extracting ..')
	[dbmain, dblitho, dblevels] = extmain.extract_NGIS_data_from_SQL_and_extents(databasename,\
	extents, database_directory = database_directory)
	print('done')
	#get absolute value of depth below ground
	dblevels['result'] = dblevels['result'].apply(lambda x: np.abs(x))
    
	dblevels['date'] = pd.to_datetime(dblevels['date'])
	dblevels = dblevels.sort_values('date')
	
	#dblitho.loc[dblitho['FromDepth']=='None','FromDepth']=-999.99 #Fixup
	dblitho.fillna(value=str('not recorded'),inplace=True) #Need to think of better method here
	dblitho['Description']=dblitho['Description'].apply(lambda x: ''.join([s for s in x if (s.isalnum() or s==' ')]).upper()) #fix bad (non alphanumeric) strings

	dbmain.to_csv('test_main.csv',index=False)
	dblevels.to_csv('test_levels.csv',index=False)
	dblitho.to_csv('test_litho.csv',index=False)
	
	if plot_litho_tables:
		plot_table(dbmain,dblitho)
		
	if plot_gwl_timeseries:
		plot_timecharts(dbmain,dblevels)
    
    
    
    
    
 

