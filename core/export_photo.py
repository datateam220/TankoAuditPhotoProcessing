import os

'''
export_photo.py
Purpose: writes a photo from an ESRI Blob field to the specified directory.

'''
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
	open(full_path, 'wb').write(attachment.tobytes())
	return full_path