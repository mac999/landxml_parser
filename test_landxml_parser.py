# title: landxml parser
# author: kang taewook
# email: laputa99999@gmail.com
# description: convert landxml to json
# license: MIT
# 
import traceback, pandas as pd
import landxml_parser as lp

def save_excel(align_dataset, fname):
	data = []
	for alignment_data in align_dataset:
		for key in alignment_data['Alignment']['attrib'].keys():
			data.append([key, alignment_data['Alignment']['attrib'][key]])

	df = pd.DataFrame(data)
	writer = pd.ExcelWriter(fname)
	df.to_excel(writer, 'alignment attrib')
	writer.save()

def test():
	try:
		lxml = lp.landxml()
		model = lxml.load('sample.xml')
		if model == None:
			print('error: load failed.')
			return
		print(model)
		lxml.save('output.json')

		for m in model:
			if 'Alignments' in m:
				align_dataset = m['Alignments']['list']
				save_excel(align_dataset, 'landxml.xlsx')
				break
	except Exception as e:
		print(traceback.format_exc())

if __name__ == "__main__":
	test()