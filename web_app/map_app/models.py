# title: data export module
# author: kang taewook
# email: laputa99999@gmail.com
# description: landxml civil model map example    
#
from django.db import models

class test_alignment(models.Model):
    # Define your fields here. For example:
    name = models.CharField(max_length=200)
    sta = models.FloatField()
    x = models.FloatField()
    y = models.FloatField()
    offset_x = models.FloatField()
    offset_y = models.FloatField()    

    class Meta:
        db_table = 'test_alignment'

class test_alignment_blocks(models.Model):
    # Define your fields here. For example:
    index = models.IntegerField()
    name = models.CharField(max_length=200)
    sta = models.FloatField()
    width1 = models.FloatField()
    width2 = models.FloatField()
    p1_x = models.FloatField()
    p1_y = models.FloatField()
    p2_x = models.FloatField()
    p2_y = models.FloatField()
    p3_x = models.FloatField()
    p3_y = models.FloatField()
    p4_x = models.FloatField()
    p4_y = models.FloatField()
    cx = models.FloatField()
    cy = models.FloatField()
    
    class Meta:
        db_table = 'test_alignment_blocks'

class test_alignment_xsections_parts(models.Model):
    sta_index = models.IntegerField()
    xsec_name = models.CharField(max_length=200)
    sta = models.FloatField()
    part_index = models.IntegerField()
    part_name = models.CharField(max_length=200)
    x = models.FloatField()
    y = models.FloatField()
    
    class Meta:
        db_table = 'test_alignment_xsections_parts'

class upload_file_model(models.Model):
	upload_file = models.FileField(upload_to='upload_files')
    