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
	align = cm.get_alignment(0)	# 첫번째 선형 얻기
	align.show_offset_objects(perp_object_point)	# 수직선을 그리고, 수직선과 교차하는 지점을 찾아서 표시

def main():
	lp = lxml.landxml()	# landxml parser 정의
	# model = lp.load('./landxml_railway_sample.xml')	# landxml 파일 로딩
	# perp_object_point = (33934.512065292125, -57758.02867007709)
	model = lp.load('./landxml_road_sample.xml')	# landxml 파일 로딩
	perp_object_point = (5373.0, 4946.0)
	# print(model)
	lp.save('output_landxml.json')	# landxml 파일을 json 파일로 변환해 저장

	cm = civil_model(model)	# 선형 계산을 위한 모델 정의
	cm.initialize()			# 선형 계산 정보 생성

	test_perp_offset(cm, perp_object_point)
	
if __name__ == "__main__":
	main()