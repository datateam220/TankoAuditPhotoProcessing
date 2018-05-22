# -*- coding: utf-8 -*-

import arcpy, os


def exportPhoto(att_data,att_name,att_id,file_location):
	'''
	att_data: blob data from ESRI feature table
	att_name: str that defines the name of the file
	att_id: int, unique id for the file
	'''
	attachment = att_data
	filenum = "ATT" + str(att_id) + "_"
	filename = filenum + att_name #removed str(att_name), probably not needed
	full_path = file_location + os.sep + filename
	if not os.path.isfile(full_path):
		open(full_path, 'wb').write(attachment.tobytes())
		return full_path
	else:
		return full_path

def build_photo_dict(photo_table,photo_folder):
	photo_dictionary = {}
	fields = ['DATA', 'ATT_NAME', 'ATTACHMENTID','REL_GLOBALID']
	#records_count = arcpy.GetCount_management(photo_table).getOutput(0)
	print("Extracting photos... This may take some time.")
	with arcpy.da.SearchCursor(photo_table, fields) as cursor:
		for record in cursor:
			attachment = record[0]
			att_name = record[1]
			att_id = record[2]
			rel_globalid = record[3]
			path = exportPhoto(attachment,att_name,att_id,photo_folder)
			if path:
				if rel_globalid not in photo_dictionary.keys():
					photo_dictionary[rel_globalid] = [path]
				else:
					photo_dictionary[rel_globalid].append(path)
	del cursor
	return photo_dictionary

def build_aud_uid_dict(photo_dictionary, collector_feature_class):
	print("Matching records to photos...")
	aud_uid_dict = {}
	fields = ['GlobalID', 'Creator','GPS_STOP']
	with arcpy.da.SearchCursor(collector_feature_class,fields) as cursor:
		for record in cursor:
			global_id = record[0]
			creator = record[1]
			GPS_STOP = record[2]
			AUD_UID = '{0}_{1}'.format(creator,GPS_STOP)
			if global_id in photo_dictionary:
				if AUD_UID not in aud_uid_dict.keys():
					aud_uid_dict[AUD_UID] = photo_dictionary[global_id]
				else:
					[aud_uid_dict[AUD_UID].append(photo) for photo in photo_dictionary[global_id]]
	del cursor
	return aud_uid_dict

def determine_number_of_photo_fields(aud_uid_dict):
	print("Determining number of necessary photo fields...")
	number_photos = 0
	for uid,photo_list in aud_uid_dict.iteritems():
		list_len = len(photo_list)
		if list_len > number_photos:
			number_photos = list_len
		else:
			continue
	return number_photos

def add_photo_fields(master_feature_class,number_photos):
	print("Adding photo fields...")
	existing_fields = [field.name for field in arcpy.ListFields(master_feature_class)]
	for i in range(number_photos):	
		photo_field ='PHOTO_{}'.format(str(i+1))
		if photo_field not in existing_fields:
			print("Adding {}".format(photo_field))
			arcpy.AddField_management(master_feature_class,photo_field,"TEXT", field_length = 500)
			print("Added {} successfully.".format(photo_field))
		else:
			continue

def insert_photos_into_master(master_feature_class,aud_uid_dict,number_photos):
	print("Populating photo fields... This may take some time.")
	fields = ['Creator','GPS_STOP']
	for i in range(number_photos):	
		photo_field ='PHOTO_{}'.format(str(i+1))
		fields.append(photo_field)
	with arcpy.da.UpdateCursor(master_feature_class,fields) as cursor:
		for record in cursor:
			photo_num = 1
			creator = record[0]
			GPS_STOP = record[1]
			AUD_UID = '{0}_{1}'.format(creator,GPS_STOP)
			if AUD_UID in aud_uid_dict.keys():
				photos = aud_uid_dict[AUD_UID]
				for photo in photos:
					if record[1+photo_num] is None:
						record[1+photo_num] = photo
						photo_num +=1
					else:
						photo_num +=1
				cursor.updateRow(record)
				photo_num = 1
			else:
				continue 
	del cursor
	print("Photo fields populated.")


