# landxml parser, civil model server and civil model web viewer
This project includes LandXML parser, civil model server and web viewer. 
- LandXML parser to read alignments, cross sections, vertical alignments and convert JSON, excel.
- Civil model server to support OpenAPI
- Civil model web viewer to support visualization for landxml in web

<p align="center">
<img height="200" src="https://github.com/mac999/landxml_parser/blob/main/civil3d_landxml.PNG"/><img height="200" src="https://github.com/mac999/landxml_parser/blob/main/landxml_sample.PNG"/>
<img height="200" src="https://github.com/mac999/landxml_parser/blob/main/json_file.PNG"/>
</p>

It is easy to develop converter from LandXML to database, file such as JSON, MongoDB, sqlite etc.</br>
<p align="center">
<img height="100" src="https://github.com/mac999/landxml_parser/blob/main/landxml_excel.PNG"/></br>
<p>

By using LandXML parser, web-based model viewer, converter, application can be developed like below.</br> 
<p align="center">
<a href="https://www.youtube.com/watch?v=TtWs6Bs8az0"><img height="300" src="https://github.com/mac999/landxml_parser/blob/main/demo_1.PNG"/></a>
</p>

# install 
## landxml parser 
```bash
pip install pandas numpy matplotlib 
```
## civil model web server and viewer 
```bash
pip install django uvicorn
```

# run
## parser
```bash
git clone https://github.com/mac999/landxml_parser
python test_landxml_parser.py
```

## civil model web server 
```bash
uvicorn open_api_server:app --reload --port 8001 --ws-max-size 16777216
```

## civil model web viewer
```bash
cd web_app
python manage.py runserver
```

# version history
- 0.1: draft version. xml parser
- 0.2: landxml parser was released. support alignment, cross section, profile 
- 0.3: web viewer for landxml was released
- TBD: TIN, clothoid etc 

# author
landxml parser develop by taewook kang(laputa99999@gmail.com).

# license
MIT license.
