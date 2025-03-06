# title: data export module
# author: kang taewook
# email: laputa99999@gmail.com
# description: landxml civil model map example    
#
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from map_app.views import import_model_files, show_map, show_test_alignment_data, show_test_alignment_blocks_data, show_test_alignment_xsections_parts_data

urlpatterns = [
    path('map/', show_map, name='show_map'),
    path('show_test_alignment_data/', show_test_alignment_data, name='show_test_alignment_data'),    
    path('show_test_alignment_blocks_data/', show_test_alignment_blocks_data, name='show_test_alignment_blocks_data'),
    path('show_test_alignment_xsections_parts_data/', show_test_alignment_xsections_parts_data, name='show_test_alignment_xsections_parts_data'),
    path('import_model/', import_model_files, name='import_model'),
    # ...
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)