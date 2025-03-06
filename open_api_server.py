# title: open api server
# author: kang taewook
# email: laputa99999@gmail.com
# 
import json, time, logging
import landxml_parser as lxml, civil_geo_engine as cge
from fastapi import FastAPI, BackgroundTasks, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from civil_geo_engine import civil_model

# Set up logging to debug
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# uvicorn open_api_server:app --reload --port 8001 --ws-max-size 16777216   # https://www.uvicorn.org
app = FastAPI()

# CORS middleware. considering security
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],  # Allows all origins
	allow_credentials=True,
	allow_methods=["*"],  # Allows all methods
	allow_headers=["*"],  # Allows all headers
)
	
def calculate_align(length):
	logger.debug('Calculation started...')

	# time.sleep(30)  # 30 seconds
	lp = lxml.landxml()	# landxml parser 정의
	model = lp.load('./landxml_railway_sample.xml')	 # railway sample에는 chain이 있음.
	lp.save('output_landxml.json')	# landxml 파일을 json 파일로 변환해 저장

	cm = civil_model(model)	# 선형 계산을 위한 모델 정의
	cm.initialize()			# 선형 계산 정보 생성

	# count total number of stations
	logger.debug(f'alignment count: {cm.alignment_count()}')
	count = 0
	for i in range(0, cm.alignment_count()):
		align = cm.get_alignment(i)
		if align == None:
			continue
		name = align.get_attrib('name')
		logger.debug(f'alignment name: {name}')
		xsections = align.get_xsections()
		logger.debug(f'xsections: {xsections}')
		count = count + len(xsections)
	logger.debug(f'stations: {count}')
	return count

@app.post("/v1/calc/align")
async def calculate_alignment(background_tasks: BackgroundTasks, length: str):
	logger.debug('Calculation started...')
	logger.debug(f'station interval length: {length}')
	# background_tasks.add_task(calculate_align, length)
	results = calculate_align(length)
	return {"results": results}

@app.websocket("/ws/align") # don't remove /ws prefix to use websocket
async def websocket_endpoint(websocket: WebSocket):
	logger.debug('Trying to connect...')
	await websocket.accept()
	logger.debug('Connection accepted.')
	with open('output_landxml.json') as json_file:
		data = json.load(json_file)
		data = json.dumps(data)

		logger.debug('Message length: ' + str(len(data)))
		CHUNK_SIZE = 64 * 1024  # 64KB
		for i in range(0, len(data), CHUNK_SIZE):
			chunk = data[i:i+CHUNK_SIZE]
			print(f'chunk: {i}')
			await websocket.send_text(chunk)
		logger.debug('JSON data sent.')

