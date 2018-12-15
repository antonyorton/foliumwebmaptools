# foliumwebmaptools
work in progress, tools for folium generation of webmaps

Started out as attempt to view Australian Groundwater Explorer public bore information on a webmap.
Raw data can be downloaded (by AUS state) from here: http://www.bom.gov.au/water/groundwater/explorer/map.shtml

Included Python files
'create_database_from_NGISdata.py'
  * Extracts relevant data from some of the raw data .csv and .shp files and allows for some cleaning
  * Creates a much easier to use SQLite table for each state
  
'extract_from_SQLdatabase.py'
  * Provides a function and method to extract hole, lithology and levels dataframes from the SQLite tables

'folium_plotter.py'
  * Some experiementation with folium plotting using altair 
        altair version 2.2.2 or higher is required

