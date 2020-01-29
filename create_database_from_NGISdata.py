
import sqlite3
import pandas as pd
import geopandas as gpd
import os

def fix_badtext_in_litholog(filename,stateID = 'SA'):
    """fixes up bad text in the South Australia, QLD 'NGIS_LithologyLog.csv' file
    filename: string.csv name of bad file eg 'NGIS_LithologyLog.csv'
    
    Do not use on NT lithology.csv files. Makes them worse
    
    returns: creates a new file names new_filename """
    
    f1 = open(filename,encoding = 'utf-8')
    str1 = str(f1.read())
    f1.close()
    if stateID == 'SA':
        str2 = str1.replace('",SAGeodata','#$$d1')
    elif stateID == 'QLD':
        str2 = str1.replace('",QLD DNRM GWDB','#$$d1')
    else:
        raise ValueError('Error: Only SA or QLD need to be put throug this function')
 
    str3 = str2.replace(',"','#&&d1')
    str4 = str3.replace('"','Quote')
    
    if stateID == 'SA':
        str5 = str4.replace('#$$d1','",SAGeodata')
    elif stateID == 'QLD':
        str5 = str4.replace('#$$d1','",QLD DNRM GWDB')

        
    str6 = str5.replace('#&&d1',',"')
    str7 = str6.replace('\'','&#39')
    
    f2 = open('new_'+filename,'w',encoding='utf-8')
    f2.write(str7)
    f2.close()
        
    return

def clean_col_strings(df,col_name,chars = '/\,:%&()-=<>.–;?‘’+~'):

    """removes specified characters from dataframe (df) column (col_name)
        Some characters were found to cause issues with folium"""

    df[col_name]=df[col_name].astype(str)
    for i in range(len(chars)):
        df[col_name] = df[col_name].apply(lambda x: x.replace(chars[i],''))

    df[col_name]=df[col_name].apply(lambda x: x.replace("'",''))

    return df

def create_SQL_from_NGIS_bore_data(state_datainput='NSW',NGISdata_dir='',SQLdata_saveto_dir=''):
    """Script to create SQL database from bom databases
       aims to rename certain columns for consistency (between states) and then save as a SQL db
       input is the state code and two directory locations
       NGISdata_directory: link to a folder containing the diffeent state folders which contain the NGIS csv, shp files"""

    dir1 = os.getcwd()
    os.chdir(NGISdata_dir)

    
    #read data into pandas
    print(' reading metadata ...')
    if state_datainput == 'NSW' or state_datainput == 'VIC':
        meta = gpd.read_file('NGIS_Bore.shp')
    else:
        meta = gpd.read_file('NGIS_Bore.shp')
    meta = pd.DataFrame(meta)
    print('done. \n reading lithology ...')
    litho = pd.read_csv('NGIS_LithologyLog.csv',error_bad_lines=False)
    print('done. \n reading gwlevel data ...')

    if state_datainput == 'NSW':
        #NSW input data
        levels = pd.read_csv('level_NSW.csv')

        #rename some columns for consistency
        meta.rename(columns={'HydroCode':'BoreID','Projecti_1':'MGAzone','RefElev':'Elevation','HeightDatu':'HeightDatum'},inplace=True)
        litho.rename(columns = {'BoreID':'not_used','HydroCode':'BoreID'},inplace=True)
        levels.rename(columns = {'bore_id':'BoreID','bore_date':'date'},inplace=True)

    elif state_datainput == 'VIC':
        #VIC input data
        levels = pd.read_csv('level_VIC.csv')

        #rename some columns for consistency
        meta.rename(columns={'HydroID':'BoreID','Projecti_1':'MGAzone','RefElev':'Elevation','HeightDatu':'HeightDatum'},inplace=True)
        levels.rename(columns = {'hydroid':'BoreID','bore_date':'date'},inplace=True)
        #NOTE: litho does not need renaming for VIC

    elif state_datainput == 'SA':
        SAlithocleaned = input('South Australia, please confirm if lithology file has been cleaned using fix_badtext_in_litholog() input y/n:  ')
        if SAlithocleaned=='y' or SAlithocleaned=='yes' or SAlithocleaned=='Y' or SAlithocleaned=='Yes':
            print('ok')
        else:
            raise ValueError('Error: South Austalia NGIS_LithologyLog.csv must be cleaned - use fix_badtext_in_litholog()')
        
        #SA input data
        levels = pd.read_csv('level_SA.csv')

        #rename some columns for consistency
        meta.rename(columns={'HydroID':'BoreID','Projecti_1':'MGAzone','RefElev':'Elevation','HeightDatu':'HeightDatum'},inplace=True)
        levels.rename(columns = {'hydroid':'BoreID','bore_date':'date'},inplace=True)
        #NOTE: litho does not need renaming for SA
        litho['Description'] = litho['Description'].apply(lambda s1: str(s1).replace('\'','&#39'))
        
        levels = levels[levels['obs_point_datum']=='SWL'].copy()
    
    elif state_datainput == 'NT':

        #NT input data
        levels = pd.read_csv('level_NT.csv')

        #rename some columns for consistency
        meta.rename(columns={'HydroID':'BoreID','Projecti_1':'MGAzone','RefElev':'Elevation','HeightDatu':'HeightDatum'},inplace=True)
        levels.rename(columns = {'hydroid':'BoreID','bore_date':'date'},inplace=True)
        #NOTE: litho does not need renaming for NT
        litho['Description'] = litho['Description'].apply(lambda s1: s1.replace('\'','&#39'))
        
        levels = levels[levels['obs_point_datum']=='SWL'].copy()

    elif state_datainput == 'QLD':
        SAlithocleaned = input('Queensland, please confirm if lithology file has been cleaned using fix_badtext_in_litholog() input y/n:  ')
        if SAlithocleaned=='y' or SAlithocleaned=='yes' or SAlithocleaned=='Y' or SAlithocleaned=='Yes':
            print('ok')
        else:
            raise ValueError('Error: Queensland NGIS_LithologyLog.csv must be cleaned - use fix_badtext_in_litholog()')
        
        #QLD input data
        levels = pd.read_csv('level_QLD.csv')

        #rename some columns for consistency
        meta.rename(columns={'HydroID':'BoreID','Projecti_1':'MGAzone','RefElev':'Elevation','HeightDatu':'HeightDatum'},inplace=True)
        levels.rename(columns = {'hydroid':'BoreID','bore_date':'date'},inplace=True)
        #NOTE: litho does not need renaming for QLD
        litho['Description'] = litho['Description'].apply(lambda s1: s1.replace('\'','&#39'))
        
        levels = levels[levels['obs_point_datum']=='SWL'].copy()

    elif state_datainput == 'WA':

        #WA input data
        levels = pd.read_csv('level_WA.csv')

        #rename some columns for consistency
        meta.rename(columns={'HydroID':'BoreID','Projecti_1':'MGAzone','RefElev':'Elevation','HeightDatu':'HeightDatum',\
        'BoreDepth':'BDnot_used','DrilledDep':'BoreDepth'},inplace=True)
        levels.rename(columns = {'hydroid':'BoreID','bore_date':'date'},inplace=True)
        #NOTE: litho does not need renaming for WA
        
        
    elif state_datainput == 'ACT':

        #ACT input data
        levels = pd.read_csv('level_ACT.csv')

        #rename some columns for consistency
        meta.rename(columns={'HydroID':'BoreID','Projecti_1':'MGAzone','RefElev':'Elevation','HeightDatu':'HeightDatum',\
        'BoreDepth':'BDnot_used','DrilledDep':'BoreDepth'},inplace=True)
        levels.rename(columns = {'hydroid':'BoreID','bore_date':'date'},inplace=True)
        #NOTE: litho does not need renaming for ACT
        litho['Description'] = litho['Description'].apply(lambda s1: s1.replace('\'','&#39'))
        

    elif state_datainput == 'TAS':

        #TAS input data
        levels = pd.read_csv('level_TAS.csv')

        #rename some columns for consistency
        meta.rename(columns={'HydroID':'BoreID','Projecti_1':'MGAzone','RefElev':'Elevation','HeightDatu':'HeightDatum',\
        'BoreDepth':'BDnot_used','DrilledDep':'BoreDepth'},inplace=True)
        levels.rename(columns = {'hydroid':'BoreID','bore_date':'date'},inplace=True)
        #NOTE: litho does not need renaming for TAS
        litho['Description'] = litho['Description'].apply(lambda s1: s1.replace('\'','&#39'))
    
    
    
    #### This part should be the same for all states in Australia

    #conn.close()  # close any open SQL connections
    ######
    database_filename = state_datainput+'BoreDatabase.db'
    
    os.chdir(SQLdata_saveto_dir)

    #create SQl connection  - creates new file if database exists (instead of overwriting)

    if database_filename in os.listdir():
        print('WARNING: Database named '+database_filename+ ' already exists')
        print('....  creating new_'+database_filename)
        database_filename = 'new_'+database_filename

    conn = sqlite3.connect(database_filename)

    print(' creating SQL table - main ...')   
    ####Condensed table only
	#meta[['BoreID','Longitude','Latitude','Easting','Northing','MGAzone',\
    #        'Elevation','HeightDatum','BoreDepth','Status']].to_sql('main',conn)
    #print (['BoreID','Longitude','Latitude','Easting','Northing','MGAzone',\
    #        'Elevation','HeightDatum','BoreDepth','Status'])
            
	####full meta table
    meta[list(meta)[0:-1]].to_sql('main',conn) #avoids adding the last column ('geometry') which causes sql issue
	
	
	
    print('done. \n creating SQL table - lithology ...')
    litho[['BoreID','FromDepth','MajorLithCode','Description']].to_sql('lithology',conn)        
    print(['BoreID','FromDepth','MajorLithCode','Description'])

    print('done. \n creating SQL table - gwlevels ...')
    levels[['BoreID','date','obs_point_datum','result']].to_sql('gwlevels',conn)     
    print(['BoreID','date','obs_point_datum','result'])

    conn.commit()
    os.chdir(dir1)
    
if __name__=="__main__":

    #location to save SQL database
    SQLdata_saveto_dir = r'C:\Users\Antony.Orton\Desktop\Python_programs\foliumwebmaptools'

    #choose state: string one of (NSW, VIC, SA, QLD, NT, WA, ACT)
    state = 'SA'
    NGISdata_dir = r'C:\Users\Antony.Orton\Desktop\Python_programs\foliumwebmaptools\databases\shp_'+state

    
    create_SQL_from_NGIS_bore_data(state_datainput=state,NGISdata_dir=NGISdata_dir,SQLdata_saveto_dir=SQLdata_saveto_dir)
