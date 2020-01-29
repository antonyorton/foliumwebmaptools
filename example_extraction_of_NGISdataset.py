"""example extraction of NGIS bore data in a specific region"""

import sys
sys.path.append(r'some\directory')
import extract_from_SQLdatabase as ext
import create_database_from_NGISdata as csql


SQLdata_saveto_dir = r'some\directory'
NGISdata_dir = r'some\directory'
state = 'NSW'

csql.create_SQL_from_NGIS_bore_data(state_datainput=state,NGISdata_dir=NGISdata_dir,SQLdata_saveto_dir=SQLdata_saveto_dir)

databasename = 'NSWBoreDatabase.db'
database_directory = r'some\directory'
extents = [100,-30,115,-32] #search extents

[dbmain, dblitho, dblevels] = ext.extract_NGIS_data_from_SQL_and_extents(databasename,\
extents, database_directory = database_directory)