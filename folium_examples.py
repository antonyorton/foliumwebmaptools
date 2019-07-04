

   
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
