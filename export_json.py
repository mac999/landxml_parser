import json, csv
import landxml_parser as lxml, civil_geo_engine as cge
from civil_geo_engine import civil_model
from tqdm import tqdm
import time

def export_align_block_model_to_json(model, align, json_path):
	"""
	Exports block model data to a JSON file, similar to export_align_block_model in export_mongodb.py.
	"""
	blocks_segments, blocks = align.get_alignment_blocks().update_blocks_segments(10.0)

	with open(json_path, 'w', encoding='utf-8') as f:
		json.dump(blocks_segments, f, ensure_ascii=False, indent=2)

	return blocks_segments, blocks

def query_blocks_in_bbox(align, query_in_bbox):
	# query blocks
	searched_segs = blocks_segments.query_blocks(query_in_bbox)
	return searched_segs

def test_query_blocks_in_bbox(blocks_segs, query_in_bbox):
	print(f"Query bbox: {query_in_bbox}")
	def point_in_bbox(x, y, bbox):
		xmin, ymin, xmax, ymax = bbox
		return xmin <= x <= xmax and ymin <= y <= ymax

	inside_points_count = 0
	outside_points_count = 0
	for i, seg in enumerate(blocks_segs):
		points = [
			(seg['p1_x'], seg['p1_y']),
			(seg['p2_x'], seg['p2_y']),
			(seg['p3_x'], seg['p3_y']),
			(seg['p4_x'], seg['p4_y'])
		]

		in_side = False
		for idx, (x, y) in enumerate(points):
			if point_in_bbox(x, y, query_in_bbox):
				in_side = True
				break
		if in_side:
			inside_points_count += 1
		else:
			outside_points_count += 1

	print(f'total segments: {len(blocks_segs)}, inside points: {inside_points_count}, outside points: {outside_points_count}')

	return [inside_points_count, outside_points_count]  

def test_query_performance(aligns):
	log_file_path = 'query_performance_log1.csv'

	# Test queries with bbox area size
	#    "p1_x": 33.52800179710506,
	#    "p1_y": 124.89826598950515, 	
	align_blocks = aligns[0].get_alignment_blocks()
	sta_list, points = aligns[0].get_polyline(20)	
	results = []
	for spatial_index in range(20):
		sta_index1 = 0
		sta_index2 = spatial_index
		if sta_index2 > len(points) - 1:
			sta_index2 = len(points) - 1

		pt1 = points[sta_index1]
		pt1 = cge.convert_coordinates(pt1[0], pt1[1])
		pt2 = points[sta_index2]
		pt2 = cge.convert_coordinates(pt2[0], pt2[1])
		query_in_bbox = (min(pt1[0], pt2[0]), min(pt1[1], pt2[1]), max(pt1[0], pt2[0]), max(pt1[1], pt2[1]))
		size_x = (query_in_bbox[2] - query_in_bbox[0])
		size_y = (query_in_bbox[3] - query_in_bbox[1]) 

		start = time.time()
		blocks_segs = align_blocks.query_blocks(query_in_bbox)
		end = time.time()
		time1 = end - start
		print(f'query {spatial_index} time performance with index: {time1}')

		cnt1 = test_query_blocks_in_bbox(blocks_segs, query_in_bbox)

		start = time.time()
		blocks_segs = align_blocks.query_blocks(query_in_bbox, use_index=False)
		end = time.time()
		time2 = end - start
		print(f'query {spatial_index} time performance without index: {time2}')

		cnt2 = test_query_blocks_in_bbox(blocks_segs, query_in_bbox)

		results.append([spatial_index, size_x, size_y, time1, time2, cnt1[0], cnt1[1], cnt2[0], cnt2[1]])

	# Write results to CSV
	with open(log_file_path, 'w', newline='', encoding='utf-8') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow(['spatial_index', 'size_x', 'size_y', 'time_with_index', 'time_without_index', 'in_cnt_with_index', 'out_cnt_with_index', 'in_cnt_without_index', 'out_cnt_without_index'])
		writer.writerows(results)

	# Test queries with different spatial index configurations
	log_file_path = 'query_performance_log2.csv'
	results = []
	for spatial_index in range(10):
		index_capacity = 10 + spatial_index * 10
		leaf_capacity = 10 + spatial_index * 10
		align_blocks.create_index(index_capacity=index_capacity, leaf_capacity=leaf_capacity)

		for index, point in enumerate(points):
			base_x, base_y = cge.convert_coordinates(point[0], point[1])
			size_x = 0.01 # 12 count at 0.001
			size_y = 0.1 # 12 count at 0.002
			query_in_bbox = (base_x, base_y, base_x + size_x, base_y + size_y)

			start = time.time()
			blocks_segs = align_blocks.query_blocks(query_in_bbox)
			end = time.time()
			time1 = end - start
			print(f'query {index} time performance with index: {time1}')

			cnt1 = test_query_blocks_in_bbox(blocks_segs, query_in_bbox)

			start = time.time()
			blocks_segs = align_blocks.query_blocks(query_in_bbox, use_index=False)
			end = time.time()
			time2 = end - start
			print(f'query {index} time performance without index: {time2}')

			cnt2 = test_query_blocks_in_bbox(blocks_segs, query_in_bbox)

			results.append([spatial_index, index, time1, time2, cnt1[0], cnt1[1], cnt2[0], cnt2[1], index_capacity, leaf_capacity])

	# Write results to CSV
	with open(log_file_path, 'w', newline='', encoding='utf-8') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow(['spatial_index', 'query_index', 'time_with_index', 'time_without_index', 'in_cnt_with_index', 'out_cnt_with_index', 'in_cnt_without_index', 'out_cnt_without_index', 'index_capacity', 'leaf_capacity'])
		writer.writerows(results)

def export_blocks():
	parser = lxml.landxml()
	model = parser.load('./landxml_road_sample.xml')
	print(model)

	start = time.time()

	cm = civil_model(model)
	cm.initialize()
	aligns = cm.get_alignments()
	if len(aligns) == 0:
		print("No alignment")
		return

	export_align_block_model_to_json(cm, aligns[0], 'block_model_output.json')
	end = time.time()
	print(f'time performance: {end - start:.6f}')

	test_query_performance(aligns)

if __name__ == "__main__":
	export_blocks()
