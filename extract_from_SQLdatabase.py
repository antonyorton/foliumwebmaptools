"""script to extract out data from a given SQL NGIS bore database within specified extents"""
import sqlite3
import pandas as pd
import os

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


if __name__=="__main__":

    database_directory='C:\\Users\\A_Orton\\Desktop\\python_codes\\3_Webmap_generator'
    databasename='SABoreDatabase.db'
    extents = [137.0936,-33.0198,137.8132,-32.4005]

    [dbmain, dblitho, dblevels] = extract_NGIS_data_from_SQL_and_extents(databasename,\
    extents, database_directory = database_directory)
        

    #rename for section plotting tool
    dfgeology = dblitho.copy()
    dfholes = dbmain.copy()

    dfgeology.rename(columns = {'BoreID':'borehole', 'FromDepth':'fromDepth', 'MajorLithCode':'material'},inplace=True)
    dfholes.rename(columns={'BoreID':'borehole','Easting':'x','Northing':'y','Elevation':'top_rl','BoreDepth':'EOH_depth'},inplace=True)            
    dfholes = dfholes[['borehole','x','y','top_rl','EOH_depth']].copy()
    dfholes['dip']=-90
    dfholes['dip_direction']=0
    dfgeology = dfgeology[['borehole','fromDepth','material']].copy()
    
    dblevels['result'] = dblevels['result'].apply(lambda x: np.abs(x))

