"""
This file contains all the common utilities for project.
"""
import os
import openpyxl
from constants import *


def check_data_type(data):
    """function to check data type and convert that into yaml data types"""

    data_type = str(type(data)).split('\'')[1]
    return DICTIONARY_DATA_TYPE[data_type]


def is_new_request(data_obj):
    """function to check the new rows to create files."""
    if data_obj.get('status') == 'new':
        return True
    return False


def check_and_create_folder(folder_path):
    """function to check file path and create if not exist"""
    if folder_path and len(folder_path) > 0 and not os.path.exists(folder_path):
        os.makedirs(folder_path)


def create_desc_obj(files_obj, rows_list):
    """function to create description object"""
    for row_val in rows_list:
        if row_val[2] != '':
            if not files_obj.get(row_val[0]).get(row_val[2], None):
                files_obj.get(row_val[0]).update({row_val[2]: {}})
            files_obj.get(row_val[0]).get(row_val[2]).update({row_val[1]: row_val[3]})
        else:
            files_obj.get(row_val[0]).update({row_val[1]: row_val[3]})
    return files_obj


def indent_description(desc_str, indent):
    """function to set indentation for multi-line description"""
    desc_str = desc_str.replace('\n', '\n{0}'.format(TWO_SPACES*indent))
    return desc_str


def create_request_params_post(request_json, file_name, param_type, required, desc_obj):
    """function to create request params for POST"""
    indent_count = 2
    schema = schema_obj(request_json, indent_count+2, required, desc_obj)
    parent_obj = '{0}- \n' \
                 '{0}{5}name: {1} \n' \
                 '{0}{5}in: {2}\n' \
                 '{0}{5}required: {3}\n' \
                 '{0}{5}schema: \n{4}'\
        .format(indent_count*TWO_SPACES, file_name, param_type, 'true', schema, TWO_SPACES)
    return parent_obj


def create_request_params_get(param_data, req_type, indent, desc_obj):
    """function to create request params for GET"""
    parent_obj = ''
    for key, value in param_data.items():
        key_type = check_data_type(value)
        parent_obj = parent_obj + '{0}- \n' \
                                  '{0}{6}name: {1} \n' \
                                  '{0}{6}in: {2}\n' \
                                  '{0}{6}description: {3}\n' \
                                  '{0}{6}required: {4}\n' \
                                  '{0}{6}type: {5}\n'\
            .format(indent*TWO_SPACES, key, req_type, 'Add description here', 'true', key_type, TWO_SPACES)
    return parent_obj


def schema_obj(request_json, indent_count, required, desc_obj):
    """function to create schema data from any kind of nested json"""
    parameters = parse_json_obj(request_json, indent_count+1, desc_obj)
    data_type = check_data_type(request_json)
    example = ((indent_count+1) * TWO_SPACES)
    for key, value in request_json.items():
        example = example + '{0}: {1}'.format(key, value) + '\n' + ((indent_count+1) * TWO_SPACES)
    return '{0}type: {1} \n' \
           '{0}properties: \n{2}\n' \
           '{0}required: {3}\n' \
           '{0}example: \n{4}' \
           .format(indent_count * TWO_SPACES, data_type, parameters, required, example)


def parse_json_obj(request_obj, indent, desc_obj):
    """function to parse nested objects """
    new_str = ''
    for key, value in request_obj.items():
        if check_data_type(value) == 'object':
            properties = parse_json_obj(value, indent + 2, desc_obj)
            desc_txt = desc_obj.get(key, DESCRIPTION_TEXT)
            if str(type(desc_txt)).split('\'')[1] == 'dict':
                desc_txt = desc_obj.get(key, DESCRIPTION_TEXT).get('heading', DESCRIPTION_TEXT)
            desc_str = indent_description(desc_txt, indent + 4)
            new_str = new_str + OBJECT_STR.format(indent * TWO_SPACES, 'object', properties, key, desc_str)
        elif check_data_type(value) == 'array':
            new_str = new_str + parse_array(value, indent, key, desc_obj.get(key, {}))
        else:
            new_str = new_str + create_inner_params(indent, value, key, desc_obj)
    return new_str


def parse_array(data_array, indent, key, desc_obj):
    """function to parse any array param"""
    new_str = ''
    field_type = check_data_type(data_array)
    if check_data_type(data_array[0]) == 'object':
        properties = parse_json_obj(data_array[0], indent+3, desc_obj)
        items = '{0}type : {1}\n' \
                '{0}properties : \n{2}'.format((indent+2) * TWO_SPACES, 'object', properties)
    else:
        items = '{0}type : {1}\n'.format((indent+3)*TWO_SPACES, check_data_type(data_array[0]))
    desc_str = indent_description(desc_obj.get('heading', DESCRIPTION_TEXT), indent+2)
    new_str = new_str + '{0}{5}:\n' \
                        '  {0}type: {1}\n' \
                        '  {0}description: | \n' \
                        '  {0}  {2}\n' \
                        '  {0}items: \n{3}\n' \
                        '  {0}example: {4}\n'.format(indent * TWO_SPACES, field_type, desc_str, items,
                                                     data_array, key)
    return new_str


def create_inner_params(indent, value, key, desc_obj):
    """function to create inner properties"""
    desc_str = indent_description(desc_obj.get(key, DESCRIPTION_TEXT), indent+2)
    field_type = check_data_type(value)
    param_str = ''
    param_str = param_str + INNER_PARAM_STR.format(key, field_type, str(value), desc_str, indent*TWO_SPACES)
    return param_str


def create_error_responses(error_list):
    """function to create any number of error responses"""
    error_string = ''
    for errors in error_list:
        error_string = error_string + (
            '{0}{1}:\n{2}description: {3}\n'.format(2*TWO_SPACES, errors[0], 3*TWO_SPACES, errors[1]))
    return error_string


def parse_success_response(data_obj, indent, desc_obj):
    """function to parse any success response"""
    resp_code = list(data_obj.keys())[0]
    schema_resp = schema_obj(data_obj[resp_code], indent+4, '', desc_obj)
    resp = ''
    resp = resp + SUCCESS_STR.format(resp_code, schema_resp)
    return resp


def create_info_details(info_obj):
    """function to create info data for swagger file"""
    info = ''
    for key, value in info_obj.items():
        if key != 'url':
            info = info + '{0}{1}: {2}\n'.format(TWO_SPACES, key, value)
    return info


def create_tags(tags_info, desc_obj):
    """function to create tags strings for swagger file"""
    info = ''
    for tags in tags_info:
        desc = indent_description(desc_obj.get(tags, DESCRIPTION_TEXT), 3)
        info = info + '{0}- name: {1}\n' \
                      '{0}{0}x-displayName: {1}\n' \
                      '{0}{0}description: |\n' \
                      '{0}{0}{0}{2}\n'.format(TWO_SPACES, tags, desc)
    return info


def create_paths(paths_info):
    """function to create path strings for swagger file"""
    info = ''
    for paths in paths_info:
        info = info + '{0}{1}:\n'\
                      '{0}{0}$ref: "{2}"\n'.format(TWO_SPACES, paths[0], "{0}.yaml".format(paths[1]))
    return info


def update_sheet_status(file_path, sheet_name, row, column):
    """function to update the status of excel column after file creation"""
    the_file = openpyxl.load_workbook(file_path)
    current_sheet = the_file.get_sheet_by_name(sheet_name)
    current_sheet[row][column].value = 'published'
    the_file.save(file_path)
    return


def update_google_sheet_status(sheet_id, range_data, sheet):
    """function to update the status of google excel column after file creation"""
    values = {"values": [["published"]]}
    sheet.values().update(spreadsheetId=sheet_id, range=range_data, valueInputOption='RAW', body=values).execute()
    return
