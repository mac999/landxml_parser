# title: civil information model
# description: version 1.1. alignment calculation. line, arc combination support.
# author: kang taewook
# email: laputa99999@gmail.com
# date: 2024.03.01
# plan: float type calculation consideration, type support etc.
# revision history:
# 2025.10.24: alignment blocks cache for query performance improvement
# 
import os, sys, re, json, random, traceback, math, pandas as pd, numpy as np, numpy as np, pyproj
import matplotlib.pyplot as plt
import landxml_parser as lxml
from rtree import index as rtree_index
from tqdm import tqdm
from scipy.spatial.distance import euclidean
from nltk.tokenize import WhitespaceTokenizer

# geometry calculation functions
sys.path.insert(0, os.path.dirname(os.getcwd()))
_precision = 0.00001

def get_angle_point(x, y, angle, distance):
	x2 = x + distance * np.cos(angle)
	y2 = y + distance * np.sin(angle)
	return (x2, y2)

def get_angle(x1, y1, x2, y2):
    pi = math.acos(-1.0)

    # Caculate the quadrant of the line.
    dx = x2 - x1
    dy = y2 - y1

    # Calculate the angle in radians for lines in the left and right quadrants
    if dx == 0 and dy == 0:
        return -1.0
    elif dy < 0 and dx == 0:
        angle_radius = pi + pi / 2
    elif dy > 0 and dx == 0:
        angle_radius = pi / 2
    else:
        angle_radius = math.atan(dy / dx)

    # Adjust the angle for different quadrants
    if dy >= 0 and dx > 0:
        pass
    elif dy < 0 and dx > 0:
        angle_radius += 2 * pi
    elif dx < 0:
        angle_radius += pi

    return angle_radius

def get_degree_angle_point(x, y, degree_angle, distance):
	radian = np.radians(degree_angle)
	return get_angle_point(x, y, radian, distance)

def point_on_arc_at_length(start, center, end, radius, arc_length, sign):
	a1 = get_angle(center[0], center[1], start[0], start[1])
	a2 = get_angle(center[0], center[1], end[0], end[1])
	# sign = 1.0 if a1 <= a2 else -1.0
	arc_length *= sign

	total_angle = math.atan2(end[1] - center[1], end[0] - center[0]) - math.atan2(start[1] - center[1], start[0] - center[0])
	total_arc_length = radius * total_angle

	fraction = arc_length / total_arc_length
	angle = math.atan2(start[1] - center[1], start[0] - center[0]) + total_angle * fraction

	x = center[0] + radius * math.cos(angle)
	y = center[1] + radius * math.sin(angle)

	return x, y

def to_degree(radian):
	return 180. * radian / math.pi

def to_radian(degree):
	return math.pi * degree / 180.

def get_azimuth_angle(x1, y1, x2, y2):
	pi = math.acos(-1.0)
	dx = x2 - x1
	dy = y2 - y1

	if dx == 0 and dy == 0:
		angle_radius = -1.0
	elif dy < 0 and dx == 0:
		angle_radius = pi + pi / 2
	elif dy > 0 and dx == 0:
		angle_radius = pi / 2
	else:
		angle_radius = math.atan(dy / dx)

	if dy >= 0 and dx > 0:
		pass
	elif dy < 0 and dx > 0:
		angle_radius += 2 * pi
	elif dx < 0:
		angle_radius += pi

	return angle_radius

def is_angle_between_angles(begin_angle, end_angle, angle):
    pi = math.acos(-1.0)

    mod = int(begin_angle / (2.0 * pi))
    begin_angle = begin_angle - mod * (2.0 * pi)

    mod = int(end_angle / (2.0 * pi))
    end_angle = end_angle - mod * (2.0 * pi)

    mod = int(angle / (2.0 * pi))
    angle = angle - mod * (2.0 * pi)

    if abs(begin_angle - angle) < 0.0001:
        return True
    if abs(end_angle - angle) < 0.0001:
        return True

    if begin_angle > end_angle:
        end_angle += (2.0 * pi)
        if angle < begin_angle:
            angle += (2.0 * pi)

    if begin_angle < angle < end_angle:
        return True

    return False

def center_point_of_polygon(vertices):
    x_sum = 0
    y_sum = 0
    num_vertices = len(vertices)

    for vertex in vertices:
        x_sum += vertex[0]
        y_sum += vertex[1]

    centroid_x = x_sum / num_vertices
    centroid_y = y_sum / num_vertices

    return (centroid_x, centroid_y)

def is_point_in_rect(point1, point2, query_point):
	return is_point_in_rectangle(point1[0], point1[1], point2[0], point2[1], query_point[0], query_point[1])

def is_point_in_rectangle(x1, y1, x2, y2, x, y):
    # Ensure that x1 <= x2 and y1 <= y2
    x1, x2 = min(x1, x2), max(x1, x2)
    y1, y2 = min(y1, y2), max(y1, y2)

    # Check if (x, y) is within the rectangle
    return x1 <= x <= x2 and y1 <= y <= y2	

def is_point_on_line(point1, point2, perp):
	if is_point_in_rect(point1, point2, perp) == False:
		return False
	sign = sign_distance_on_line(point1, point2, perp)
	if math.fabs(sign) < _precision:
		return True
	return False

def arc_diff(begin_angle, end_angle):
	# Normalize angles to be in the range [0, 360)
	pi2 = math.pi * 2.0	
	begin_angle = begin_angle % pi2
	end_angle = end_angle % pi2

	# Ensure the angles are in the same direction
	if begin_angle <= end_angle:
		angle_diff = end_angle - begin_angle
	else:
		angle_diff = pi2 - begin_angle + end_angle

	return angle_diff

def arc_length(begin_angle, end_angle, radius):
	angle_diff = arc_diff(begin_angle, end_angle)
	arc_length = math.radians(angle_diff) * radius
	return arc_length

def sign_distance(a, b, c, p):
	d = math.sqrt(a*a + b*b)
	if d == 0.0:
		lp = 0.0
	else:
		lp = (a * p[0] + b * p[1] + c) / d
	return lp

def equal(a, b):
	return abs(a - b) < _precision

def sign_point_on_line(point1, point2, Point):	# left side < 0.0. right side > 0.0
	if equal(point1[0], Point[0]) and equal(point1[1], Point[1]):
		return 0
	if equal(point2[0], Point[0]) and equal(point2[1], Point[1]):
		return 0

	def get_angle(x1, y1, x2, y2):
		return math.atan2(y2 - y1, x2 - x1)

	def diff_angle(base_angle, target_angle):
		pi = math.acos(-1.0)
		diff = target_angle - base_angle
		if diff < 0.0:
			diff += 2.0 * pi
		return diff

	def interval_angle(base_angle, target_angle):
		pi = math.acos(-1.0)
		mod = int(base_angle / (2.0 * pi))
		base_angle = base_angle - mod * (2.0 * pi)

		mod = int(target_angle / (2.0 * pi))
		target_angle = target_angle - mod * (2.0 * pi)

		target_angle1 = diff_angle(base_angle, target_angle)
		return target_angle1

	line_angle = get_angle(point1[0], point1[1], point2[0], point2[1])
	angle1 = get_angle(point1[0], point1[1], Point[0], Point[1])
	angle2 = get_angle(Point[0], Point[1], point2[0], point2[1])

	dInterval1 = interval_angle(line_angle, angle1)
	dInterval2 = interval_angle(line_angle, angle2)

	PI = math.acos(-1.0)
	if equal(dInterval1, 0):
		dInterval1 = (PI * 2.0) - dInterval1
	if equal(dInterval2, 0):
		dInterval2 = (PI * 2.0) - dInterval2
	if equal(abs(dInterval1), abs(dInterval2)):
		return 0

	if abs(dInterval1) > abs(dInterval2):
		return 1  # Right    
	return -1

def sign_distance_on_line(line_point1, line_point2, point):
	direction = sign_point_on_line(line_point1, line_point2, point)
	if direction == 0:
		return 0.0

	if math.fabs(line_point1[0] - line_point2[0]) < _precision and math.fabs(line_point1[1] <= line_point2[1]) < _precision:
		return 0.0

	x = point[0]
	y = point[1]
	x1 = line_point1[0]
	y1 = line_point1[1]
	x2 = line_point2[0]
	y2 = line_point2[1]

	if x1 <= x2:
		a = 1
		b = 0
		c = -x1
	else:
		m = (y2 - y1) / (x2 - x1)
		a = -m
		b = 1
		c = -y1 + (m * x1)

	dist = abs(a * x + b * y + c) / math.sqrt(a * a + b * b)
	dist *= float(direction)

	return dist

def get_perp_point_on_line(line_point1, line_point2, point):
	dist = sign_distance_on_line(line_point1, line_point2, point)
	if dist == 0.0:
		return line_point1
	
	angle = get_angle(line_point1[0], line_point1[1], line_point2[0], line_point2[1])
	
	if angle < 0.:
		return line_point1

	s = 1.0 if dist > 0. else -1.0
	pi = math.acos(-1.0) / 2.0
	pi *= s
	angle += pi
	dist = math.fabs(dist)

	join_point = [point[0] + math.cos(angle) * dist, point[1] + math.sin(angle) * dist]
	return join_point

def convert_coordinates(x, y, from_crs='epsg:2097', to_crs='epsg:4326'): # 중부원점 TM 좌표계. https://www.osgeo.kr/17
	proj1 = pyproj.Proj(from_crs)        
	proj2 = pyproj.Proj(to_crs)

	transform = pyproj.Transformer
	trans = transform.from_crs(from_crs, to_crs)
	x2, y2 = trans.transform(x, y)
		
	return x2, y2

# align_segment
class align_segment:
	_type = ""
	_points = []
	_attrib = {}
	_length = 0.0

	def __init__(self, type, points, attrib):
		self._type = type
		self._points = points
		self._attrib = attrib

		for index, point_data in enumerate(self._points):
			type = lxml.get_key_in_dict(point_data, 0)
			if type == None:
				continue
			self._points[index] = point_data[type]['points'][0]

		self._length = self.get_length()

	def get_length(self):
		if self._points == None or len(self._points) == 0:
			return 0.0
		if self._attrib == None:
			return 0.0

		if self._type == "Line":
			if len(self._points) < 2:
				return 0.0
			point1 = self._points[0]
			point2 = self._points[1]
			return euclidean(point1, point2)

		if self._type == "Curve": # arc
			if 'length' in self._attrib:
				return float(self._attrib['length'])
			return 0.0

	def get_circle(self):
		if self._points == None or len(self._points) == 0:
			return None
		if self._attrib == None:
			return None	

		if self._type == "Curve": # arc
			if len(self._points) < 3:
				return None

			c = self._points[1]
			radius = euclidean(c, self._points[0])
			return c[0], c[1], radius
		return None

	def get_station_position(self, target_station):
		if self._points == None or len(self._points) == 0:
			return None
		if self._attrib == None:
			return None	
		
		if self._type == "Line":
			if len(self._points) < 2:
				return None
			
			point1 = self._points[0]
			point2 = self._points[1]
			
			angle = get_angle(point1[0], point1[1], point2[0], point2[1])
			distance = euclidean(point1, point2)
			x, y = get_angle_point(point1[0], point1[1], angle, target_station)
			return (x, y)
		
		if self._type == "Curve": # arc
			if len(self._points) < 3:
				return None

			x1, y1 = self._points[0]
			cx, cy = self._points[1]
			x2, y2 = self._points[2]

			sign = 1.0
			if self._attrib["rot"] == "ccw":
				sign = -1.0
			x, y = point_on_arc_at_length((x1, y1), (cx, cy), (x2, y2), float(self._attrib['radius']), target_station, sign)

			return (x, y)	

	def get_perp_points(self, object_point, offset_range):
		if self._points == None or len(self._points) == 0:
			return None
		if self._attrib == None:
			return None	
		
		if self._type == "Line":
			if len(self._points) < 2:
				return None
			
			point1 = self._points[0]
			point2 = self._points[1]

			perp = get_perp_point_on_line(point1, point2, object_point)
			offset = sign_distance_on_line(point1, point2, object_point)
			dist = euclidean(point1, perp)
			length = euclidean(point1, point2)
			is_on_line = is_point_on_line(point1, point2, perp)
			if is_on_line and dist <= length and math.fabs(offset) <= offset_range:
				return [dist, perp[0], perp[1], offset]
			return None
		
		if self._type == "Curve": # arc
			if len(self._points) < 3:
				return None

			c = self._points[1]
			a1 = get_angle(c[0], c[1], self._points[0][0], self._points[0][1])
			a2 = get_angle(c[0], c[1], self._points[2][0], self._points[2][1])
			radius = euclidean(c, self._points[0])
			dist = arc_length(a1, a2, radius)

			perp_angle = get_angle(c[0], c[1], object_point[0], object_point[1])
			perp = get_angle_point(c[0], c[1], perp_angle, radius)
			offset = euclidean(c, object_point) - radius

			is_in_angles = is_angle_between_angles(a1, a2, perp_angle)
			if self._attrib["rot"] == "ccw":
				is_in_angles = is_in_angles == False
				offset = -offset
			if is_in_angles and math.fabs(offset) <= offset_range:
				return [dist, perp[0], perp[1], offset]
			return None

		return None

class cross_section_part:
	_attrib = {}
	_points_data = []
	def __init__(self, attrib, points_data):
		self._attrib = attrib
		self._points_data = points_data

	def get_attrib(self, key):
		if key in self._attrib:
			return self._attrib[key]
		return None

	def get_points_data(self):
		return self._points_data

	def get_points(self):
		points = []
		for point_data in self._points_data:
			type = lxml.get_key_in_dict(point_data, 0)
			if type == None:
				continue
			points.extend(point_data[type]['points'])
		return points

class cross_section:
	_attrib = None
	_crs_data = None
	_part_list = []

	def __init__(self, attrib, crs_data):
		self._attrib = attrib
		self._crs_data = crs_data

	def initialize(self, cross_sect_part_list):
		self._part_list = []
		for surf in cross_sect_part_list:
			type = lxml.get_key_in_dict(surf, 0)
			if type == None:
				continue
			
			surf_data = surf[type]
			attrib = surf_data['attrib']
			points_data_list = surf_data['list']
				
			part = None
			if 'CrossSectSurf' in surf:
				part = cross_section_part(attrib, points_data_list)

			elif 'DesignCrossSectSurf' in surf:
				part = cross_section_part(attrib, points_data_list)

			self._part_list.append(part)

	def get_attrib(self, key):
		if key in self._attrib:
			return self._attrib[key]
		return None

	def get_parts(self):
		return self._part_list

	def plot_parts(self, plt, ax):
		cmap = plt.get_cmap('viridis')  # Get the colormap

		for index, part in enumerate(self._part_list):
			name = part.get_attrib('name')
			points = part.get_points()
			x = [position[0] for position in points]
			y = [position[1] for position in points]
			ax.scatter(x, y, c='r', s=2)

			# index color
			color = cmap(index / len(self._part_list))			
			ax.plot(x, y, c=color, linestyle='-', linewidth=1)			

class alignment_blocks: # block cache
	_blocks = []
	_blocks_segments = []
	_align = None
	_index = None

	def __init__(self, align):
		self._align = align

	def get_blocks_segments(self):
		return self._blocks_segments

	def update_blocks_segments(self, sta_resolution=10.0, begin_sta = 0.0, end_sta = 0.0, offset=-20.0, offset_step=10, max_offset=10):
		if self._align == None:
			return self._blocks_segments

		self._blocks = self._align.get_block_points(sta_resolution, begin_sta, end_sta, offset, offset_step, max_offset)
		offset_x, offset_y = 0, 0

		self._blocks_segments = []
		for block in tqdm(self._blocks):
			index = block['index']
			sta = block['sta']
			width1 = block['width1']
			width2 = block['width2']

			km = sta / 1000.0
			meter = sta % 1000.0
			sta_name = f'{km:.0f}+{meter}' # 1+140, 2+250, 3+360, ...

			vertics = block['vertices']
			x = [position[0] for position in vertics]
			y = [position[1] for position in vertics]
			gsr80_points = convert_coordinates(x, y)
			gsr80_points = [[x + offset_x, y + offset_y] for x, y in zip(gsr80_points[0], gsr80_points[1])]

			center = block['center']
			center_x, center_y = center
			center_gsr80 = convert_coordinates([center_x], [center_y])
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
			self._blocks_segments.append(data)

		self.create_index()

		return self._blocks_segments, self._blocks

	def create_index(self, index_capacity=100, leaf_capacity=100):
		"""
		Build a spatial index (R-tree) for block points (p1, p2, p3, p4).
		Each block's corner points are indexed for fast bbox queries.
		Uses rtree library (pip install rtree).
		"""
		if len(self._blocks_segments) == 0:
			return None

		# Create R-tree index. https://rtree.readthedocs.io/en/latest/
		p = rtree_index.Property()
		p.dimension = 2
		p.index_capacity = index_capacity
		p.leaf_capacity = leaf_capacity
		p.near_minimum_overlap_factor = int(index_capacity / 2)
		idx = rtree_index.Index(properties=p)

		# Index each block's p1, p2, p3, p4 as points
		for seg_index, block in enumerate(self._blocks_segments):
			pts = [
				(block['p1_x'], block['p1_y']),
				(block['p2_x'], block['p2_y']),
				(block['p3_x'], block['p3_y']),
				(block['p4_x'], block['p4_y'])
			]
			for i, (x, y) in enumerate(pts):
				# Insert as a point bbox (x, y, x, y), id is (block_id, i)
				idx.insert(seg_index * 10 + i, (x, y, x, y), obj=seg_index)

		self._index = idx
		return self._index

	def query_blocks(self, query_in_bbox, use_index=True):
		if use_index and self._index != None:
			# Use R-tree index for fast query
			result_blocks = []
			bbox = query_in_bbox
			matches = self._index.intersection(bbox, objects=True)
			seen_indices = set()
			for match in matches:
				block_index = match.object
				if block_index not in seen_indices:
					result_blocks.append(self._blocks_segments[block_index])
					seen_indices.add(block_index)
			return result_blocks

		result_blocks = []
		for block in self._blocks_segments:
			p1 = (block['p1_x'], block['p1_y'])
			p2 = (block['p2_x'], block['p2_y'])
			p3 = (block['p3_x'], block['p3_y'])
			p4 = (block['p4_x'], block['p4_y'])

			query_pt1 = (query_in_bbox[0], query_in_bbox[1])
			query_pt2 = (query_in_bbox[2], query_in_bbox[3])

			if is_point_in_rect(query_pt1, query_pt2, p1) or is_point_in_rect(query_pt1, query_pt2, p2) or is_point_in_rect(query_pt1, query_pt2, p3) or is_point_in_rect(query_pt1, query_pt2, p4):
				result_blocks.append(block)

		return result_blocks

class alignment:
	_model_data = None
	_align_data = None
	_align_segments = []
	_cross_sects = []

	_alignment_blocks = None

	def __init__(self, model, align_data):
		self._model_data = model
		self._align_data = align_data
		self._align_segments = []
		self._cross_sects = []
		self._alignment_blocks = alignment_blocks(self)		

	def initialize(self):
		self._align_ips = []
		if self._align_data == None:
			return False
		
		obj_list = self._align_data['list']
		for obj in obj_list:
			if 'CoordGeom' in obj:
				geo_data = obj['CoordGeom']
				self._init_geometry(geo_data)
			elif 'CrossSects' in obj:
				crs_data = obj['CrossSects']
				self._init_cross_sects(crs_data)
			elif 'Profile' in obj:
				profile_data = obj['Profile']
				self._init_profile(profile_data)

	def _init_geometry(self, geo_data):	# protect member
		self._align_ips = []

		geom_list = geo_data['list']
		for coord_geom in geom_list:
			type = lxml.get_key_in_dict(coord_geom, 0)
			if type == None:
				continue

			curve_data = coord_geom[type]
			points_data = curve_data['list']

			attrib = curve_data['attrib']
			seg = align_segment(type, points_data, attrib)
			self._align_segments.append(seg)

	def _init_cross_sects(self, align_obj_data):	# protect member
		self._align_ips = []

		crs_list = align_obj_data['list']
		for crs_data in crs_list:
			type = lxml.get_key_in_dict(crs_data, 0)
			if type == None:
				continue

			cross_sect_data = crs_data[type]		# CrossSect	
			attrib = cross_sect_data['attrib']
			cs = cross_section(attrib, cross_sect_data)

			cross_sect_part_list = cross_sect_data['list']
			cs.initialize(cross_sect_part_list)

			self._cross_sects.append(cs)			

	def _init_profile(self, geo_data):	# protect member
		self._align_ips = []

		geom_list = geo_data['list']
		for coord_geom in geom_list:
			type = lxml.get_key_in_dict(coord_geom, 0)
			if type == None:
				continue

	def get_attrib(self, key):
		if key in self._align_data['attrib']:
			return self._align_data['attrib'][key]
		return None

	def get_length(self):
		length = 0.0
		for seg in self._align_segments:
			length += seg._length

		return length

	def get_station_position(self, target_station):
		if self._align_segments == None or len(self._align_segments) == 0:
			return None

		for seg in self._align_segments:
			if target_station <= seg._length:
				return seg.get_station_position(target_station)
			target_station -= seg._length

		return None

	def get_xsections(self):
		return self._cross_sects
	
	def get_polyline(self, resolution, begin = 0.0, end = 0.0):
		length = self.get_length()
		sta_list = []
		points = []
		sta = 0.0
		while sta < length:
			if (begin == 0.0 and end == 0.0) or (begin != 0.0 and begin <= sta) or end != 0.0 and sta <= end:
				pass
			else:
				sta += resolution
				continue

			x, y = self.get_station_position(sta)
			sta_list.append(sta)
			points.append((x, y))

			print(str(sta) + ": " + str(x) + ", " + str(y))
			sta += resolution
		return sta_list, points
	
	def get_offset_polyline(self, resolution, offset, begin = 0.0, end = 0.0):
		length = self.get_length()
		sta_list = []
		points = []
		sta = 0.0
		while sta < length:
			if (begin == 0.0 and end == 0.0) or (begin != 0.0 and begin <= sta) or end != 0.0 and sta <= end:
				pass
			else:
				sta += resolution
				continue

			x, y = self.get_perpendicular_point(sta, offset)
			sta_list.append(sta)
			points.append((x, y))

			print(str(sta) + ": " + str(x) + ", " + str(y))
			sta += resolution
		return sta_list, points

	def get_station_tangent(self, station):
		x1, y1 = self.get_station_position(station)
		x2, y2 = self.get_station_position(station + 0.001)

		angle = get_angle(x1, y1, x2, y2)
		return x1, y1, angle

	def get_perpendicular_point(self, station, side_offset):
		x, y, tangent = self.get_station_tangent(station)
		angle = tangent 
		if side_offset >= 0.0:
			angle += math.pi / 2.0
		else:
			angle -= math.pi / 2.0

		perp_point = get_angle_point(x, y, angle, math.fabs(side_offset))
		return perp_point

	def get_perp_points(self, object_point, offset_range):
		if self._align_segments == None or len(self._align_segments) == 0:
			return None

		object_sta_offset_list = []
		index = 0
		cur_length = 0.0
		while index < len(self._align_segments):
			seg = self._align_segments[index]
			perp_point = seg.get_perp_points(object_point, offset_range)

			if perp_point != None and len(perp_point):
				perp_point[0] = perp_point[0] + cur_length
				object_sta_offset_list.append(perp_point)
			seg_len = seg.get_length()
			cur_length += seg_len
			index += 1

		return object_sta_offset_list

	def get_block_points(self, resolution, begin_sta = 0.0, end_sta = 0.0, offset=-20.0, offset_step=10, max_offset=10):  # from -20 to 10, 10 step, make blocks.
		sta_list, pline = self.get_polyline(resolution, begin_sta, end_sta)		# 선형을 resolution미터 간격으로 좌표 생성

		blocks = []
		while offset <= max_offset:
			sta_list, pline = self.get_offset_polyline(resolution, offset, begin_sta, end_sta)		# 선형을 10미터 간격으로 좌표 생성
			offset_sta_list, offset_pline = self.get_offset_polyline(resolution, offset + offset_step, begin_sta, end_sta)	# 선형에서 옵셋 선형 생성
			x = [position[0] for position in offset_pline]
			y = [position[1] for position in offset_pline]

			# 중심선형과 옵센된 선형 사이에 사각 격자를 생성해 그려줌
			index = 1
			count = len(pline)
			while index < count:
				x1, y1 = pline[index - 1]
				x2, y2 = pline[index]
				x3, y3 = offset_pline[index - 1]
				x4, y4 = offset_pline[index]
						
				vertices = [(x1, y1), (x2, y2), (x4, y4), (x3, y3)]

				block = {
					"index": index,
					"sta": sta_list[index],
					"width1": offset,
					"width2": offset + offset_step,
					"vertices": vertices,
					"center": center_point_of_polygon(vertices),
				}
				blocks.append(block)

				index += 1

			offset += offset_step
		return blocks

	def get_alignment_blocks(self):
		return self._alignment_blocks

	def plot_offset_polyline(self, plt, ax, resolution, begin = 0.0, end = 0.0):
		sta_list, pline = self.get_polyline(resolution, begin, end)		# 선형을 resolution미터 간격으로 좌표 생성

		x = [position[0] for position in pline]
		y = [position[1] for position in pline]
		ax.scatter(x, y, c='r', s=2)
		ax.plot(x, y, c='b', linestyle='-', linewidth=1)

		offset = -20.0
		offset_step = 10.0
		max_offset = 10.0
		while offset <= max_offset:
			sta_list, pline = self.get_offset_polyline(resolution, offset, begin, end)		# 선형을 10미터 간격으로 좌표 생성
			offset_sta_list, offset_pline = self.get_offset_polyline(resolution, offset + offset_step, begin, end)	# 선형에서 옵셋 선형 생성
			x = [position[0] for position in offset_pline]
			y = [position[1] for position in offset_pline]
			ax.scatter(x, y, c='r', s=2)
			ax.plot(x, y, c='b', linestyle='-', linewidth=1)

			# 중심선형과 옵센된 선형 사이에 사각 격자를 생성해 그려줌
			index = 1
			count = len(pline)
			while index < count:
				x1, y1 = pline[index - 1]
				x2, y2 = pline[index]
				x3, y3 = offset_pline[index - 1]
				x4, y4 = offset_pline[index]
						
				vertices = [(x1, y1), (x2, y2), (x4, y4), (x3, y3)]
				x_coordinates, y_coordinates = zip(*vertices)
				x_coordinates += (x_coordinates[0],)
				y_coordinates += (y_coordinates[0],)
				# rgb = (float(index) / float(count), 1.0, 0.1)
				rgb = (0.1, random.uniform(0.0, 1.0), random.uniform(0.0, 1.0))
				ax.fill(x_coordinates, y_coordinates, facecolor=rgb, edgecolor='orange', alpha=0.5)  # alpha controls transparency

				cx, cy = center_point_of_polygon(vertices)
				r = random.uniform(0.0, 1.0) * offset_step / 2.0
				rgb = (random.uniform(0.0, 1.0), 0.3, 0.3)
				circle = plt.Circle((cx, cy), r, color=rgb, fill=True)
				ax.add_artist(circle)

				index += 1

			offset += offset_step

	def show_polyline(self):
		# Plot the alignment
		import matplotlib.pyplot as plt
		_, ax = plt.subplots()

		plt.xlabel('X Coordinate')
		plt.ylabel('Y Coordinate')

		self.plot_offset_polyline(plt, ax, 10)

		ax.set_aspect('equal', 'box')	# axes.axis('equal')
		plt.show() 
		input()

	def plot_align_curve(self, plt, ax):
		index = 0
		colors = ['b', 'c', 'k', 'g', 'm', 'y']	# https://matplotlib.org/stable/gallery/color/named_colors.html
		while index < len(self._align_segments):
			seg = self._align_segments[index]

			if seg._type == "Curve":			
				col = colors[index % 6]
	
				cx, cy, r = seg.get_circle()
				circle = plt.Circle((cx, cy), r, color=col, fill=False)
				ax.add_artist(circle)

				x, y = seg._points[0]
				ax.scatter(x, y, c=col, marker='+', s=30)
				x, y = seg._points[2]
				ax.scatter(x, y, c=col, marker='+', s=30)

			index += 1

	def show_offset_objects(self, object_point=(33934.512065292125, -57758.02867007709), offset_range=500):
		sta_list, pline = self.get_polyline(10)		# Generate coordinates at 10-meter intervals along the alignment

		# Plot the alignment
		import matplotlib.pyplot as plt
		_, ax = plt.subplots()

		plt.xlabel('X Coordinate')
		plt.ylabel('Y Coordinate')
		x = [position[0] for position in pline]
		y = [position[1] for position in pline]
		ax.scatter(x, y, c='g',  marker='.', s=10)
		ax.plot(x, y, c='black', linestyle='-', linewidth=1)

		ax.scatter(object_point[0], object_point[1], color='darkgreen', marker='o', s=50)

		sta_offset = self.get_perp_points(object_point, offset_range)
		print(sta_offset)
			
		x = [position[1] for position in sta_offset]
		y = [position[2] for position in sta_offset]
		ax.scatter(x, y, c='r', marker='^', s=50)

		self.plot_align_curve(plt, ax)

		ax.set_aspect('equal', 'box')	# axes.axis('equal')

		plt.show() 
		input()

class civil_model:
	_model_data = None
	_aligns = []
	# TBD: TIN, coordinate etc.

	def __init__(self, model):
		self._model_data = model

	def find_object(self, name):
		if self._model_data == None:
			return None

		for civil_obj in self._model_data:
			if name in civil_obj:
				return civil_obj[name]
		return None

	def initialize(self):
		try:
			self._aligns = []
			aligns = self.find_object('Alignments')
			if aligns == None:
				return False
			
			for align_data in aligns['list']:
				align_data = align_data['Alignment']
				align_obj = alignment(self._model_data, align_data)
				align_obj.initialize()
				self._aligns.append(align_obj)
		except Exception as e:
			traceback.print_exc()
			return False
		
		return True

	def get_alignments(self):
		return self._aligns

	def find_alignment(self, name):
		if self._aligns == None:
			return None
		
		for align in self._aligns:
			if align._align_data['attrib']['name'] == name:
				return align
		return None
	
	def get_alignment(self, index):
		if self._aligns == None:
			return None
		if len(self._aligns) <= index:
			return None
		return self._aligns[index]
	
	def alignment_count(self):
		if self._aligns == None:
			return None
		return len(self._aligns)
