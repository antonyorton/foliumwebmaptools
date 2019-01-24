"""script to extract out data from a given SQL NGIS bore database within specified extents"""
import sqlite3
import pandas as pd
import numpy as np
import os
import pyproj

#Extract lithography and gwlevels into pandas dataframes from specified extents
def extract_NGIS_data_from_SQL_and_extents(databasename, extents, database_directory = ''):
    """extract out data from a given SQL NGIS bore database within specified extents
        extents: [longmin,latmin,longmax,matmax]
        
        returns list of pandas dataframes [dfmain, dflitho, dflevels]
    """
    dir1 = os.getcwd()
    os.chdir(database_directory)
    conn=sqlite3.connect(databasename)



    #method 2 (fast) - SQL based create a temp table /s inside the extents  (don't commit)
    conn.execute("create table temp_main as select * from main where Longitude > "+str(extents[0])+" AND \
                Longitude < "+str(extents[2])+" AND Latitude > "+str(extents[1])+" AND Latitude < "+str(extents[3]))

    conn.execute("create table temp_lithology as select g.BoreID, g.FromDepth, g.MajorLithCode, g.Description from lithology as g \
                join temp_main as tm on tm.BoreID = g.BoreID")
                  
    conn.execute("create table temp_gwlevels as select g.BoreID, g.date, g.obs_point_datum, g.result from gwlevels as g \
                join temp_main as tm on tm.BoreID = g.BoreID")
          
    dbmain = pd.read_sql("select * from temp_main",conn)
    dblitho = pd.read_sql("select * from temp_lithology",conn)
    dblevels = pd.read_sql("select * from temp_gwlevels",conn)           
               
    conn.execute("drop table temp_main")
    conn.execute("drop table temp_lithology")
    conn.execute("drop table temp_gwlevels")  
    conn.commit()
    conn.close()

    os.chdir(dir1)
    return [dbmain, dblitho, dblevels]


def latlong_to_MGA(Lon_Lat):
    """Transforms from long_Lat to MGA94
    
    INPUT:
    Lon_Lat: 2d array-like of longitudes (col1) and latitude (col2)
    
    RETURNS:    
    array:  column 1: Easting, 2: Northing, 3: MGAzone
    
        """
        
    Lon_Lat=np.array(Lon_Lat)
    MGA=np.zeros((np.shape(Lon_Lat)[0],3))
    
    wgs84=pyproj.Proj('+init=EPSG:4326')
    
    for i in range(len(Lon_Lat)):
        zone=int(Lon_Lat[i,0]/6)+31
        mga94=pyproj.Proj('+init=EPSG:283'+str(zone))  
        x,y=pyproj.transform(wgs84,mga94,Lon_Lat[i,0],Lon_Lat[i,1]) #convert to mga94
        MGA[i,0]=x
        MGA[i,1]=y
        MGA[i,2]=zone
        
    return MGA
    
    
def MGA_to_latlong(eastings,northings,MGAzone):
    """ get latlong from MGA coords
    
    INPUT:
    eastings: 1D array-like, eastings coordinates
    northings: 1D array-like northings coordinates
    MGAzone: (integer) Australian MGAzone (49,50,51,52,53,54,55 or 56)

    RETURNS: 
    A 2-tuple, 1. Longitudes 2. Latitudes
          
        """
    
    if type(eastings) == pd.DataFrame or type(eastings) == pd.Series:
        eastings = np.array(eastings)
    
    if type(northings) == pd.DataFrame or type(northings) == pd.Series:
        northings = np.array(northings)
    
    
    if not int(MGAzone) in np.arange(49,57):
        raise ValueError('Error: MGA zone must be between 49 and 56')
    
    wgs84=pyproj.Proj('+init=EPSG:4326')
    mga94=pyproj.Proj('+init=EPSG:283'+str(MGAzone))

    longitude,latitude = pyproj.transform(mga94,wgs84,eastings,northings) #convert to mga94

    return (longitude,latitude)

	
	
	
if __name__=="__main__":

	database_directory=r'C:\Users\Antony.Orton\Desktop\Python_programs\foliumwebmaptools'
	databasename='NSWBoreDatabase.db'
	extents = [149.774579,-30.46434,150.157727,-30.160842]

	[dbmain, dblitho, dblevels] = extract_NGIS_data_from_SQL_and_extents(databasename,\
	extents, database_directory = database_directory)

	#get absolute value of depth below ground
	dblevels['result'] = dblevels['result'].apply(lambda x: np.abs(x))

	#rename for section plotting tool (not needed for NGIS webmap plots)
	#dfgeology = dblitho.copy()
	#dfholes = dbmain.copy()

	#attach longitude and latitude (not needed for NGIS webmap plots)
	#MGAzone = int(latlong_to_MGA([[0.5*(extents[0]+extents[2]),0.5*(extents[1]+extents[3])]])[0,2])
	#dfholes['Longitude'],dfholes['Latitude'] = MGA_to_latlong(dfholes['Easting'],dfholes['Northing'],MGAzone)

	#Rename and extract certain columns only (not needed for NGIS webmap plots)
	#dfgeology.rename(columns = {'BoreID':'borehole', 'FromDepth':'fromDepth', 'MajorLithCode':'material'},inplace=True)
	#dfholes.rename(columns={'BoreID':'borehole','Easting':'x','Northing':'y','Elevation':'top_rl','BoreDepth':'EOH_depth'},inplace=True)            
	#dfholes = dfholes[['borehole','x','y','top_rl','EOH_depth']].copy()
	#dfholes['dip']=-90
	#dfholes['dip_direction']=0
	#dfgeology = dfgeology[['borehole','fromDepth','material']].copy()

	
	

