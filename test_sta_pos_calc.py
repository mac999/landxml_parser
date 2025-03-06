# title: civil information model
# author: kang taewook
# email: laputa99999@gmail.com
# description: version 1.0. alignment calculation. line, arc combination support.
# 
import os, sys, re, json, random, traceback, math, pandas as pd, numpy as np, numpy as np
import matplotlib.pyplot as plt
import landxml_parser as lxml, civil_geo_engine as cge
from civil_geo_engine import civil_model

def test_station_position_calculation(cm):
	align = cm.get_alignment(0)	
	if align == None:
		print("No alignment")
		return

	def plot_text(ax, text, x, y, angle, font_size = 12, horizontal_alignment = 'left', vertical_alignment = 'center'):
		angle = cge.to_degree(angle)  # Text angle in degrees
		ax.text(x, y, text, rotation=angle, fontsize=font_size, ha=horizontal_alignment, va=vertical_alignment)

	sta_list, points = align.get_polyline(20)	
	sta_offset_list, offset_points = align.get_offset_polyline(20, 10)	
	sta_df = pd.DataFrame({'station': sta_list})
	points_df = pd.DataFrame(points, columns=['x', 'y'])

	merged_df = pd.concat([sta_df, points_df], axis=1)
	merged_df.to_csv('output.csv', index = False)	

	# Plot the alignment
	import matplotlib.pyplot as plt
	_, ax = plt.subplots()

	plt.xlabel('X Coordinate')
	plt.ylabel('Y Coordinate')

	x = [position[0] for position in points]
	y = [position[1] for position in points]
	ax.scatter(x, y, c='r', s=2)
	ax.plot(x, y, c='b', linestyle='-', linewidth=1)

	for index, point in enumerate(points):
		ax.plot([point[0], offset_points[index][0]], [point[1], offset_points[index][1]], c='g', linestyle='-', linewidth=1)
		angle = cge.get_angle(point[0], point[1], offset_points[index][0], offset_points[index][1])	+ math.pi 
		plot_text(ax, str(sta_list[index]), point[0], point[1], angle, 10, 'left', 'bottom')

	ax.set_aspect('equal', 'box')	# axes.axis('equal')
	plt.show() 
	input()

def main():
	lp = lxml.landxml()	
	# model = lp.load('./landxml_railway_sample.xml')	
	model = lp.load('./landxml_road_sample.xml')	
	# print(model)
	lp.save('output_landxml.json')	

	cm = civil_model(model)
	cm.initialize()			

	test_station_position_calculation(cm)
	
if __name__ == "__main__":
	main()