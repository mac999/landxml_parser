# title: data export module
# author: kang taewook
# email: laputa99999@gmail.com
# description: version 1.0. alignment calculation. line, arc combination support.
# 
# instructions:
# 1. install sqlite3
# 2. install sqlite3 python module
# 3. run this script
import json, time
import landxml_parser as lxml, civil_geo_engine as cge
from tqdm import tqdm
from pyproj import CRS, Transformer
from civil_geo_engine import civil_model
import sqlite3

def export_align_model(model, aligns):
	# export sqlite3
	conn = sqlite3.connect('civilmodel.db')
	cursor = conn.cursor()

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

	cursor.execute('''CREATE TABLE IF NOT EXISTS test_alignment (name text, sta real, x real, y real, offset_x real, offset_y real)''')

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
		
		cursor.execute('''INSERT INTO test_alignment VALUES (?, ?, ?, ?, ?, ?)''', (data['name'], data['sta'], data['x'], data['y'], data['offset_x'], data['offset_y']))

	conn.commit()
	conn.close()

def test():
	parser = lxml.landxml()
	# model = parser.load('landxml_railway_sample.xml')
	model = parser.load('./landxml_road_sample.xml')	
	print(model)

	# time performance test
	start = time.time()

	cm = civil_model(model)	# 선형 계산을 위한 모델 정의
	cm.initialize()			# 선형 계산 정보 생성
	aligns = cm.get_alignments()

	export_align_model(cm, aligns)

	end = time.time()
	print(f"Time performance: {end - start}")

if __name__ == "__main__":
	test()