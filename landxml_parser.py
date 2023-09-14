# title: landxml parser
# author: kang taewook
# email: laputa99999@gmail.com
# description: convert landxml to json
# 
import os, sys, re, json, math, traceback, pandas as pd, numpy as np, numpy as np
import xml.etree.ElementTree as elemTree
from nltk.tokenize import WhitespaceTokenizer

sys.path.insert(0, os.path.dirname(os.getcwd()))

def import_json(fname): 
	data = None
	with open(fname) as f:
		data = json.load(f)
	return data

def get_xml_tag_name(tag):
	index = tag.find("}") 
	if index >= 0:
		tag = tag[index + 1: len(tag)]

	return tag

def get_key_in_dict(dict_data, index):
	list = [i for i in dict_data.keys()]
	if len(list) <= index:
		return None
	return list[index]
	
class XML_parser:
	_find = 0
	_nodes = []
	
	def clear_finall_node(self):
		self._nodes.clear()
		
	def add_findall_node(self, node):
		for n in self._nodes:
			if n == node:
				return
		self._nodes.append(node)
		return

	def is_match_attrib(self, node, attr):
		i = 0
		for key in attr:
			try:
				# print("cond: " + key)
				value = attr[key]
				if node.attrib[key].find(value) >= 0: 
					continue
				return False
			except:
				return False
			i = i + 1
		print("* matched. " + str(node.attrib))
		return True

	def findall(self, node, tag, attr = ""):
		#tag_cond = {'base_tag': 'CrossSect', 'name': "0+040.00"}
		for child in node:
			try:
				if child.tag.find(tag) >= 0:
					# print(str(find) + ".tag: " + child.tag + ": " + str(child.attrib))
					if self.is_match_attrib(child, attr):
						self.add_findall_node(child)
						return child					
			except ValueError:
				pass
			result = self.findall(child, tag, attr)
			if result != None:
				self.add_findall_node(child)
				return result
			self._find = self._find + 1
		return None

class landxml:
	_model_data = None
	def __init__(slef):
		pass

	def load(self, fpath):
		try:
			tree = elemTree.parse(fpath)
			root = tree.getroot()        

			model = self.parsing(root)
			self._model_data = model
			return model
		except Exception as e:
			traceback.print_exc()
			pass
		return None

	def save(self, fpath):
		try:
			if self._model_data == None:
				return
			
			with open(fpath, 'w') as json_file:
				json.dump(self._model_data, json_file, indent = 2)
		except Exception as e:
			traceback.print_exc()
			pass

	def get_points_in_text(self, text):
		tk = WhitespaceTokenizer()
		tokens = tk.tokenize(text)
		pcd = []
		i = 0
		count = round(len(tokens) / 2)
		for i in range(count):
			x = float(tokens[i * 2])
			y = float(tokens[i * 2 + 1])
			pcd.append((x, y))
		return pcd

	def get_attrib_text(self, node):
		tag = get_xml_tag_name(node.tag)
		print(tag, node.attrib)
		data = {}
		data[tag] = {}
		data[tag]['attrib'] = node.attrib
		if node.text == None:
			data[tag]['text'] = ""
		else:
			data[tag]['text'] = node.text.replace('\t', '')
			data[tag]['text'] = data[tag]['text'].replace('\n', '')
		data[tag]['list'] = []

		return tag, node.attrib, node.text, data
	
	def parsing_curve(self, node, model):
		for child in node:
			tag, attrib, text, data = self.get_attrib_text(child)
			if text != None:
				data[tag]['points'] = self.get_points_in_text(text)
			model.append(data)

			if tag.find("Start") >= 0:
				pass
			elif tag.find("Center") >= 0:
				pass
			elif tag.find("End") >= 0:
				pass
			elif tag.find("PI") >= 0:
				pass

		return model

	def parsing_curve_set(self, node, model):
		for child in node:
			tag, attrib, text, data = self.get_attrib_text(child)

			if child.tag.find("Line") >= 0 or child.tag.find("Curve") >= 0:
				model.append(data)
				self.parsing_curve(child, data[tag]['list'])

		return model

	def parsing_cross_sect_surf(self, node, model):
		for child in node:
			tag, attrib, text, data = self.get_attrib_text(child)

			if child.tag.find("PntList2D") < 0:
				continue

			data[tag]['points'] = self.get_points_in_text(text)
			model.append(data)

		return model

	def parsing_design_cross_sect_surf(self, node, model):
		for child in node:
			tag, attrib, text, data = self.get_attrib_text(child)

			if child.tag.find("CrossSectPnt") < 0:
				continue

			data[tag]['points'] = self.get_points_in_text(text)	# TBD
			model.append(data)

		return model

	def parsing_cross_sect(self, node, model):
		for child in node:
			tag, attrib, text, data = self.get_attrib_text(child)

			if child.tag.find("DesignCrossSectSurf") >= 0:
				model.append(data)
				self.parsing_design_cross_sect_surf(child, data[tag]['list'])
			elif child.tag.find("CrossSectSurf") >= 0:
				model.append(data)
				self.parsing_cross_sect_surf(child, data[tag]['list'])

		return model

	def parsing_cross_sects(self, node, model):
		for child in node:
			tag, attrib, text, data = self.get_attrib_text(child)

			if child.tag.find("CrossSect") >= 0:
				model.append(data)
				self.parsing_cross_sect(child, data[tag]['list'])

		return model

	def parsing_prof_surf(self, node, model):
		for child in node:
			tag, attrib, text, data = self.get_attrib_text(child)

			if child.tag.find("PntList2D") >= 0:
				data[tag]['points'] = self.get_points_in_text(text)
				model.append(data)

		return model

	def parsing_prof_align(self, node, model):
		for child in node:
			tag, attrib, text, data = self.get_attrib_text(child)

			if child.tag.find("PVI") >= 0:
				data[tag]['points'] = self.get_points_in_text(text)
				model.append(data)
			elif child.tag.find("ParaCurve") >= 0:
				data[tag]['points'] = self.get_points_in_text(text)
				model.append(data)

		return model

	def parsing_profile(self, node, model):
		for child in node:
			tag, attrib, text, data = self.get_attrib_text(child)

			if child.tag.find("ProfSurf") >= 0:
				model.append(data)
				self.parsing_prof_surf(child, data[tag]['list'])
			elif child.tag.find("ProfAlign") >= 0:
				model.append(data)
				self.parsing_prof_align(child, data[tag]['list'])

		return model

	def parsing_coordgeom(self, node, model):
		for child in node:
			tag, attrib, text, data = self.get_attrib_text(child)

			if tag.find("CoordGeom") >= 0:
				model.append(data)
				self.parsing_curve_set(child, data[tag]['list'])
			elif tag.find("CrossSects") >= 0:
				model.append(data)
				self.parsing_cross_sects(child, data[tag]['list'])
			elif tag.find("Profile") >= 0:
				model.append(data)
				self.parsing_profile(child, data[tag]['list'])

		return model

	def parsing_alignment(self, node, model):
		for child in node:
			tag, attrib, text, data = self.get_attrib_text(child)

			if tag.find("Alignment") >= 0:
				model.append(data)
				self.parsing_coordgeom(child, data[tag]['list'])	

		return model

	def parsing(self, node):
		model = []

		try:
			for child in node:
				tag, attrib, text, data = self.get_attrib_text(child)

				if tag.find("Project") >= 0:
					pass   
				elif tag.find("Units") >= 0:
					pass   
				elif tag.find("Application") >= 0:
					pass
				elif tag.find("Alignments") >= 0:
					model.append(data)
					self.parsing_alignment(child, data[tag]['list'])
				elif tag.find("Roadways") >= 0:
					pass   
				elif tag.find("Surfaces") >= 0:
					pass   
		except Exception as e:
			traceback.print_exc()
			pass			
		return model
	
def test():
	lxml = landxml()
	model = lxml.load('sample.xml')
	print(model)
	lxml.save('output.json')

if __name__ == "__main__":
	test()