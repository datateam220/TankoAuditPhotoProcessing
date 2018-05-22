# -*- coding: utf-8 -*-

import os, arcpy
import assc_photos as PhotoAnalysis

photo_table = r'U:\PhotoProcessing\working\TankoAuditPhotoProcessing\tests\sample_data\LBNL_test_data\LBNL_Photos_2.gdb\TankoDefault_DD__ATTACH'
photo_folder = r'U:\PhotoProcessing\working\TankoAuditPhotoProcessing\tests\sample_data\LBNL_test_data\PHOTOS'
collector_fc = r'U:\PhotoProcessing\working\TankoAuditPhotoProcessing\tests\sample_data\LBNL_test_data\LBNL_Photos_2.gdb\TankoDefault_DD'
master_fc = r'U:\PhotoProcessing\working\TankoAuditPhotoProcessing\tests\sample_data\LBNL_test_data\LBNL_test.gdb\LBNL_Master_Audit'

photo_dictionary = PhotoAnalysis.build_photo_dict(photo_table,photo_folder)

aud_uid_dict = PhotoAnalysis.build_aud_uid_dict(photo_dictionary,collector_fc)

number_photo_fields = PhotoAnalysis.determine_number_of_photo_fields(aud_uid_dict)

PhotoAnalysis.add_photo_fields(master_fc,number_photo_fields)

PhotoAnalysis.insert_photos_into_master(master_fc,aud_uid_dict,number_photo_fields)