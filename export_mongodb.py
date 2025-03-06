# title: data export module
# author: kang taewook
# email: laputa99999@gmail.com
# description: version 1.0. alignment calculation. line, arc combination support.
# 
# instructions:
# 1. install mongo db community server (https://www.mongodb.com/try/download/community)
# 2. install pymongo
# 3. run this script
# 4. check the mongodb database
import json, time
import landxml_parser as lxml, civil_geo_engine as cge
from tqdm import tqdm
from pyproj import CRS, Transformer
from civil_geo_engine import civil_model
from pymongo import MongoClient

def export_landxml(parser):
	# export mongodb
	client = MongoClient('localhost', 27017)  # Connect to your MongoDB
	db = client['landxml_db']  # Choose your database
	collection = db['landxml_collection']  # Choose your collection

	models = parser.get_models_data()

	for model in models:
		align = model['Alignments']        
		collection.insert_one(align)

	# commit
	client.close()

def export_align_model(model, aligns):
	# export mongodb
	client = MongoClient('localhost', 27017)  # Connect to your MongoDB
	db = client['civil_model_db']             # Choose your database
	collection = db['test_alignment']    # Choose your collection  
	
	if len(aligns) == 0:
		print("No alignment")
		return
	align = aligns[0]

	sta_list, points = align.get_polyline(20.0)	# 선형을 10미터 스테이션 간격으로 좌표점을 생성
	sta_offset_list, offset_points = align.get_offset_polyline(20, 10)	

	x = [position[0] for position in points]
	y = [position[1] for position in points]

	offset_x = [position[0] for position in offset_points]
	offset_y = [position[1] for position in offset_points]

	gsr80_points = cge.convert_coordinates(x, y)
	gsr80_offset_points = cge.convert_coordinates(offset_x, offset_y)

	offset_x, offset_y = 4.590738489, 2.193844253 # landxml_road_sample LandXML은 공사원점에서 진행하므로, 임의로 테스트위해, KICT 연천 기준으로 이동
	gsr80_points = [[x + offset_x, y + offset_y] for x, y in zip(gsr80_points[0], gsr80_points[1])]
	gsr80_offset_points = [[x + offset_x, y + offset_y] for x, y in zip(gsr80_offset_points[0], gsr80_offset_points[1])]

	for index, sta in tqdm(enumerate(sta_list)):
		km = sta / 1000.0
		meter = sta % 1000.0
		sta_name = f'{km:.0f}+{meter}' # 1+140, 2+250, 3+360, ...

		data = {
			"name": sta_name,
			'sta': float(sta),
			"x": gsr80_points[index][0],
			"y": gsr80_points[index][1], 
			'offset_x': gsr80_offset_points[index][0], 
			'offset_y': gsr80_offset_points[index][1]
		}
		collection.insert_one(data)

	# commit
	client.close()

def export_align_block_model(model, aligns):
	# export mongodb
	client = MongoClient('localhost', 27017)  # Connect to your MongoDB
	db = client['civil_model_db']             # Choose your database
	collection = db['test_alignment_blocks']    # Choose your collection  
	
	if len(aligns) == 0:
		print("No alignment")
		return
	align = aligns[0]
	blocks = align.get_block_points(10.0)

	for block in tqdm(blocks):
		index = block['index']
		sta = block['sta']
		width1 = block['width1']
		width2 = block['width2']

		km = sta / 1000.0
		meter = sta % 1000.0
		sta_name = f'{km:.0f}+{meter}' # 1+140, 2+250, 3+360, ...

		offset_x, offset_y = 4.590738489, 2.193844253 # landxml_road_sample LandXML은 공사원점에서 진행하므로, 임의로 테스트위해, KICT 연천 기준으로 이동

		vertics = block['vertices']
		x = [position[0] for position in vertics]
		y = [position[1] for position in vertics]
		gsr80_points = cge.convert_coordinates(x, y)
		gsr80_points = [[x + offset_x, y + offset_y] for x, y in zip(gsr80_points[0], gsr80_points[1])]

		center = block['center']
		center_x, center_y = center
		center_gsr80 = cge.convert_coordinates([center_x], [center_y])
		center_gsr80 = [center_gsr80[0][0] + offset_x, center_gsr80[1][0] + offset_y]

		data = {
			"index": index,
			"name": sta_name,
			'sta': float(sta),
			"width1": width1,
			"width2": width2,
			"p1_x": gsr80_points[0][0],
			"p1_y": gsr80_points[0][1],
			"p2_x": gsr80_points[1][0],
			"p2_y": gsr80_points[1][1],
			"p3_x": gsr80_points[2][0],
			"p3_y": gsr80_points[2][1],
			"p4_x": gsr80_points[3][0],
			"p4_y": gsr80_points[3][1],
			"cx": center_gsr80[0],
			"cy": center_gsr80[1]
		}

		collection.insert_one(data)

	# commit
	client.close()

def test():
	parser = lxml.landxml()
	# model = parser.load('landxml_railway_sample.xml')
	model = parser.load('./landxml_road_sample.xml')	
	print(model)

	start = time.time()

	cm = civil_model(model)	# 선형 계산을 위한 모델 정의
	cm.initialize()			# 선형 계산 정보 생성
	aligns = cm.get_alignments()

	# export_align_model(cm, aligns)
	export_align_block_model(cm, aligns)

	end = time.time()
	print('time performance: ', end - start)	

if __name__ == "__main__":
	test()