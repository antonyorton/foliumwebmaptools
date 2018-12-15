import folium
from folium import Element, Html
import folium.plugins as fp
import altair as alt
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import html
import shutil
alt.renderers.enable('notebook')


def plot_table(dbmain, dbdata , idcol = 'BoreID',depthcol = 'FromDepth', datacol = 'Description', endholecol = 'BoreDepth'):

    """ Plot dataframe data on folium
    dbmain: dataframe with coordinates (Latitude and Longitude)
    dbdata: dataframe with data (specified in depthcol and datacol)
    datacol: string or list of column names from dbdata to plot against depthcol
    """
    
    centro = [dbmain['Latitude'].mean(),dbmain['Longitude'].mean()]
    map = folium.Map(location= centro,tiles = 'OpenStreetMap',zoom_start=12)

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
            popup=folium.Popup('<b>'+'bore:  </b>'+str(bores[i])+'<b>'+'       EOH(m): </b>'+str(endofhole)[0:5]+'<br>'+lithodata.iloc[0:25].to_html(index = False))
            folium.Marker(location=[latitude1,longitude1],popup=popup).add_to(map)              
            if np.mod(i,5)==0: 
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
    map = folium.Map(location= centro,tiles = 'OpenStreetMap',zoom_start=12)

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
        '<br><b>Date: </b>'+levdata.sort_values(datecol).iloc[-1][datecol]+\
        '<br><b>Bore depth: </b>'+str(endofhole)+' m<br>'
        if len(levdata)>1:  #plot chart if more than on reading - string to popup html file (from disk) to new window with specified size
            #htmlstring = """<a href="#" target="_blank" onClick="window.open('C:/Users/A_Orton/Desktop/python_codes/1_DEM_plotting_and_section/ARUP_version_testing/images/well"""+str(i)+""".html','pagename','resizable,height=400,width=520'); return false;">Groundwater plot</a>"""
            htmlstring = """<a href="#" target="_blank" onClick="window.open('WMPtt18images/"""+str(bores[i])+""".html','pagename','resizable,height=400,width=520'); return false;">Groundwater plot</a>"""
            h1=Html(s1+htmlstring.replace('\'','&#39'),script=True) #Critical to remove single quotes from the string by replacing \' with &#39
            popup=folium.Popup(h1)
        else:    #else display value only
            popup = str(s1)
        folium.Marker(location=[latitude1,longitude1],popup=popup).add_to(map)              
        print(i)        

    map.save('tester1.html')


    
    
    
    
    
    
    
    
    
    
    
    
###### Folium html examples

#Bad string characters - must use string.replace('\'','&#39') to repair
folium.Marker(location=[43.653509, -79.384079],popup=str('This won\'t work')).add_to(map)

#Single image popup
folium.Marker(location=[43.653409, -79.384079],
              popup=str('<img src="C:/Users/A_Orton/Desktop/python_codes/SQLite/images/example_01.png" alt="Mountain">')).add_to(map)

#Link to folder or file location          
folium.Marker(location=[43.54209, -79.32079],
              popup=str('<a href="C:/Users/A_Orton/Desktop/python_codes/pdf_extractor/pdfs">file link</a>')).add_to(map)
 
#General wording styles and mixed with images
s1=  '<!DOCTYPE html>'\
    '<title>Page Title</title>'\
    '<h1>This is a heading</h1>'\
    '<p>This is a paragraph.</p>'\
    '<img src="C:/Users/A_Orton/Desktop/python_codes/SQLite/images/snowhero.png" alt="Mountain">'\
    '<p>Above is a snow man.</p>'
folium.Marker(location=[43.46209, -79.32079], popup=str(s1)).add_to(map)
              
#Popup html file (from disk, eg an altair chart pre-saved to html file) in same browser window with no resizing"
s1='<a href="/html/tags/" target="C:/Users/A_Orton/Desktop/python_codes/SQLite/images/test.html">HTML Tags</a>'
folium.Marker(location=[43.46209, -79.32079], popup=str(s1)).add_to(map)         

#insert target="_blank" to have new browser window with no re-sizing
s1=str('<a href="C:/Users/A_Orton/Desktop/python_codes/SQLite/images/test.html" target="_blank">View chart</a>')

#Popup in a new window of smaller size
htmlstring = """<a href="#" target="_blank" onClick="window.open('C:/Users/A_Orton/Desktop/python_codes/SQLite/images/test.html','pagename','resizable,height=400,width=520'); return false;">Groundwater plot</a>"""
h1=Html(htmlstring.replace('\'','&#39'),script=True) #Critical to remove single quotes from the string by repla
popup=folium.Popup(h1)


