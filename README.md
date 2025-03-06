# landxml parser, civil model server and civil model web viewer
This project includes LandXML parser, civil model generation from LandXML, civil model server and web viewer. 
- LandXML parser to read alignments, cross sections, vertical alignments and convert JSON, excel.
- Civil model server to support OpenAPI
- Civil model web viewer to support visualization for landxml in web
- Export landxml to sqlite, mongodb

<p align="center">
<img height="200" src="https://github.com/mac999/landxml_parser/blob/main/doc/civil3d_landxml.PNG"/><img height="200" src="https://github.com/mac999/landxml_parser/blob/main/doc/landxml_sample.PNG"/>
<img height="200" src="https://github.com/mac999/landxml_parser/blob/main/doc/json_file.PNG"/>
</p>

It is easy to develop converter from LandXML to database, file such as JSON, MongoDB, sqlite etc.</br>
<p align="center">
<img height="100" src="https://github.com/mac999/landxml_parser/blob/main/doc/landxml_excel.PNG"/></br>
<p>

By using LandXML parser, web-based model viewer, converter, application can be developed like below.</br> 
<p align="center">
<a href="https://www.youtube.com/watch?v=TtWs6Bs8az0"><img height="300" src="https://github.com/mac999/landxml_parser/blob/main/doc/demo_1.PNG"/></a>
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

---
# utility tools
## export landxml to database 
### **1. `export_sqlite.py`** (SQLite-based export)

#### **Purpose:**
- Reads alignment data from LandXML.
- Converts alignment coordinates.
- Stores alignment station points into a SQLite database (`civilmodel.db`).

#### **Key Components:**
- **SQLite3 Integration:**  
  ```python
  conn = sqlite3.connect('civilmodel.db')
  cursor = conn.cursor()
  ```
  - Connects to SQLite and prepares a table (`test_alignment`).
  
- **Alignment Processing:**  
  ```python
  sta_list, points = align.get_polyline(20.0)
  sta_offset_list, offset_points = align.get_offset_polyline(20, 10)
  ```
  - Generates station points and offset points every **20 meters**.

- **Coordinate Transformation:**
  ```python
  gsr80_points = cge.convert_coordinates(x, y)
  gsr80_offset_points = cge.convert_coordinates(offset_x, offset_y)
  ```
  - Converts coordinates to a specific reference system.

- **Data Storage in SQLite:**
  ```python
  cursor.execute('''INSERT INTO test_alignment VALUES (?, ?, ?, ?, ?, ?)''', ...)
  conn.commit()
  ```
  - Stores alignment data with station name, coordinates, and offsets.

- **Execution Flow:**
  - Loads LandXML.
  - Initializes civil model.
  - Extracts alignments and exports them to SQLite.

---

### **2. `export_xsections_mongodb.py`** (MongoDB-based cross-section export)

#### **Purpose:**
- Extracts **cross-section data** from alignments.
- Stores cross-section parts in **MongoDB**.

#### **Key Components:**
- **MongoDB Connection:**  
  ```python
  client = MongoClient('localhost', 27017)
  db = client['civil_model_db']
  collection = db['test_alignment_xsections_parts']
  ```
  - Connects to MongoDB and selects the **test_alignment_xsections_parts** collection.

- **Cross-Section Processing:**  
  ```python
  xsections = align.get_xsections()
  ```
  - Retrieves all cross-sections.

- **Data Storage in MongoDB:**  
  ```python
  collection.insert_one(data)
  ```
  - Stores each cross-section's station index, name, part details, and coordinates.

- **Execution Flow:**
  - Loads LandXML.
  - Extracts alignments and cross-sections.
  - Saves data in MongoDB.

---

### **3. `export_mongodb.py`** (MongoDB-based alignment export)

#### **Purpose:**
- Extracts and exports **alignment data** and **alignment blocks**.
- Stores the results in **MongoDB**.

#### **Key Components:**
- **MongoDB Connection:**
  ```python
  client = MongoClient('localhost', 27017)
  db = client['civil_model_db']
  collection = db['test_alignment']
  ```
  - Connects to the **civil_model_db** database.

- **Alignment Processing:**
  ```python
  sta_list, points = align.get_polyline(20.0)
  ```
  - Generates points every **20 meters**.

- **Storing Data:**
  ```python
  collection.insert_one(data)
  ```
  - Saves alignment data, including:
    - Station name (`1+140`, `2+250`, etc.).
    - Coordinates (`x`, `y`).
    - Offset values.

- **Block Processing:**
  ```python
  blocks = align.get_block_points(10.0)
  ```
  - Extracts block-level alignment data at **10-meter** intervals.

- **Execution Flow:**
  - Loads LandXML.
  - Extracts alignments and blocks.
  - Saves results in MongoDB.

---

### **Summary**
| Script | Database | Purpose |
|--------|----------|---------|
| `export_sqlite.py` | SQLite | Exports alignment data to a **local SQLite DB**. |
| `export_xsections_mongodb.py` | MongoDB | Stores **cross-section** data in MongoDB. |
| `export_mongodb.py` | MongoDB | Exports **alignments and blocks** to MongoDB. |


# author
landxml parser develop by taewook kang(laputa99999@gmail.com).

# license
MIT license.
