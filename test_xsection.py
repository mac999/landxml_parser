# title: civil information model
# author: kang taewook
# email: laputa99999@gmail.com
# description: version 1.0. alignment calculation. line, arc combination support.
# 
import os, sys, re, json, random, traceback, math, pandas as pd, numpy as np, numpy as np
import matplotlib.pyplot as plt
import landxml_parser as lxml, civil_geo_engine as cge
from civil_geo_engine import civil_model

def plot_xsection(cm):
	align = cm.get_alignment(0)	# 첫번째 선형 얻기
	if align == None:
		print("No alignment")
		return
	
	xsections = align.get_xsections()
	num_subplot = len(xsections) > 6 and 6 or len(xsections)
	fig, axes = plt.subplots(2, 3, figsize=(20, 20))

	fig.suptitle('Cross Section')
	
	for index, xsec in enumerate(xsections):
		if index >= 6:
			break
		name = xsec.get_attrib('name')
		sta_name = xsec.get_attrib('sta')

		ax = axes[index//3][index%3]
		ax.set_aspect('equal', 'box')
		ax.set_title(name)
		ax.grid(True)
		xsec.plot_parts(plt, ax)
		
	plt.show()

	input()

def main():
	lp = lxml.landxml()	# landxml parser 정의
	model = lp.load('./landxml_railway_sample.xml')	# landxml 파일 로딩
	# model = lp.load('./landxml_road_sample.xml')	 

	cm = civil_model(model)	# 선형 계산을 위한 모델 정의
	cm.initialize()			# 선형 계산 정보 생성

	plot_xsection(cm)
	
if __name__ == "__main__":
	main()