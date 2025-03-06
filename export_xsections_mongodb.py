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

def export_xsection(cm, aligns):
	client = MongoClient('localhost', 27017)  # Connect to your MongoDB
	db = client['civil_model_db']             # Choose your database
	collection = db['test_alignment_xsections_parts']    # Choose your collection  
	
	if len(aligns) == 0:
		print("No alignment")
		return
	align = aligns[0]
	xsections = align.get_xsections()

	for sta_index, xsec in tqdm(enumerate(xsections)):
		xsec_name = xsec.get_attrib('name')
		sta_name = xsec.get_attrib('sta')

		parts = xsec.get_parts()
		for part_index, part in enumerate(parts):
			part_name = part.get_attrib('name')
			points = part.get_points()

			for pt_index, point in enumerate(points):
				x = point[0]
				y = point[1]
				data = {
					'sta_index': sta_index,
					'xsec_name': xsec_name,
					'sta': float(sta_name),
					'part_index': part_index,
					'part_name': part_name,
					'x': x,
					'y': y
				}

				collection.insert_one(data)
	client.close()

def test():
	parser = lxml.landxml()
	model = parser.load('landxml_railway_sample.xml')
	print(model)

	start = time.time()

	cm = civil_model(model)	# 선형 계산을 위한 모델 정의
	cm.initialize()			# 선형 계산 정보 생성
	aligns = cm.get_alignments()

	export_xsection(cm, aligns)

	end = time.time()
	print('time performance: ', end - start)

if __name__ == "__main__":
	test()