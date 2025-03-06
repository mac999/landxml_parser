# title: data export module
# author: kang taewook
# email: laputa99999@gmail.com
# description: landxml civil model map example    
#
import logging, os
from django.core.serializers import serialize
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.core.files.storage import default_storage
from pymongo import MongoClient
from .models import test_alignment, test_alignment_blocks, test_alignment_xsections_parts
from .forms import FilesForm
from .models import upload_file_model

logger = logging.getLogger('loggers')

def show_map(request):
	return render(request, 'map.html')

def import_model_files(request):
	form = FilesForm(request.POST, request.FILES)

	if request.method == 'POST':
		files = request.FILES.getlist('upload_file')

		for f in files:
			upload_model = upload_file_model(upload_file = f)
			upload_model.save()

			# read the file as text
			file_path = default_storage.open(upload_model.upload_file.name)
			file_content = file_path.read().decode('utf-8')
			file_path.close()

			# save the file_content to the mongodb
			client = MongoClient('mongodb://localhost:27017/civil_model_db')
			db = client.civil_model_db
			collection = db['landxml']
			collection.insert_one({'name': f.name, 'content': file_content})

	context = {'form': form}
	return render(request, "import_model.html", context)

def show_test_alignment_data(request):
	logger.info('test')
	logger.info('debug.request: %s', request)

	queryset = test_alignment.objects.all()
	data = list(queryset.values())

	''' data = {
		"landxml": [
			{
				"name": "landxml1",
				"description": "landxml1 description"
			},
			{
				"name": "landxml2",
				"description": "landxml2 description"
			}
		]
	} '''

	if os.environ and 'SERVER_PROTOCOL' in os.environ:	# 2024.10.8. https://www.mongodb.com/community/forums/t/djongo-notimplementederror-database-objects-do-not-implement-truth-value-testing-or-bool/188912/4
		print(f'SERVER_PROTOCOL: {os.environ["SERVER_PROTOCOL"]}')
	return JsonResponse(data, safe=False) 

def show_test_alignment_blocks_data(request):
	try:
		names = test_alignment_blocks.objects.values('name')
		queryset = test_alignment_blocks.objects.all()
		data = list(queryset.values())
		return JsonResponse(data, safe=False)
	except Exception as e:
		logger.error('error: %s', e)
		return JsonResponse([], safe=False)


def show_test_alignment_xsections_parts_data(request):
	try:
		sta_index = request.GET.get('sta_index')
		queryset = test_alignment_xsections_parts.objects.filter(sta_index=sta_index)
		data = list(queryset.values())
		return JsonResponse(data, safe=False)
	except Exception as e:
		logger.error('error: %s', e)
		return JsonResponse([], safe=False)