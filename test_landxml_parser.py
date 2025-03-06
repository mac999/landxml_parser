import landxml_parser as lxml

def test():
	parser = lxml.landxml()
	# model = parser.load('landxml_railway_sample.xml')	
	model = parser.load('./landxml_road_sample.xml')	
	print(model)
	parser.save('output_landxml.json')

if __name__ == "__main__":
	test()