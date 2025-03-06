# title: civil information model
# author: kang taewook
# email: laputa99999@gmail.com
# description: version 1.0. alignment calculation. line, arc combination support.
# 
import os, sys, re, json, random, traceback, math, pandas as pd, numpy as np, numpy as np
import matplotlib.pyplot as plt
import landxml_parser as lxml, civil_geo_engine as cge
from civil_geo_engine import civil_model

def test_perp_offset(cm, perp_object_point):	
	align = cm.get_alignment(0)	# Get the first alignment
	align.show_offset_objects(perp_object_point)	# Draw a perpendicular line and mark the intersection points

def main():
	lp = lxml.landxml()	
	# model = lp.load('./landxml_railway_sample.xml')	
	# perp_object_point = (33934.512065292125, -57758.02867007709)
	model = lp.load('./landxml_road_sample.xml')	
	perp_object_point = (5373.0, 4946.0)
	# print(model)
	lp.save('output_landxml.json')	

	cm = civil_model(model)	
	cm.initialize()			

	test_perp_offset(cm, perp_object_point)
	
if __name__ == "__main__":
	main()