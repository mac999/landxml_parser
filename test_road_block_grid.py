# title: civil information model
# author: kang taewook
# email: laputa99999@gmail.com
# description: version 1.0. alignment calculation. line, arc combination support.
# 
import os, sys, re, json, random, traceback, math, pandas as pd, numpy as np, numpy as np
import matplotlib.pyplot as plt
import landxml_parser as lxml, civil_geo_engine as cge
from civil_geo_engine import civil_model

def test_polyline_grid(cm):
	align = cm.get_alignment(0)	# Get the first alignment
	if align == None:
		print("No alignment")
		return
	align.show_polyline()

def main():
	lp = lxml.landxml()	# Define landxml parser
	# model = lp.load('./landxml_railway_sample.xml')	# Load landxml file
	model = lp.load('./landxml_road_sample.xml')	 
	# print(model)
	lp.save('output_landxml.json')	# Convert landxml file to json and save

	cm = civil_model(model)	# Define model for alignment calculation
	cm.initialize()			# Generate alignment calculation information

	test_polyline_grid(cm)
	
if __name__ == "__main__":
	main()