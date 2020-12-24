"""
This is the entry point of utility which calls all the subsequent functions.
"""
from __future__ import print_function
import sys
import csv
import json
import xlrd
import pickle
import logging
from os import path
from loggers import log_message
from utility import *
from constants import *

desc_obj = {}
sheet = {}
SWAGGER_SPREADSHEET_ID = ''
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

LOGGER = logging.getLogger("root")
logger = log_message('INFO', "root")


def create_paths_by_excel(file_name):
    """function to read data from excel"""
    if path.exists(file_name):
        sheets_list = xlrd.open_workbook(file_name)
        swagger_data = None
        sheet_data = None
        desc_data = None
        for sheets in sheets_list.sheets():
            if sheets.name == 'data':
                sheet_data = sheets
            if sheets.name == 'swagger':
                swagger_data = sheets
            if sheets.name == 'description':
                desc_data = sheets
        if desc_data:
            global desc_obj
            col_file = desc_data.col_values(0)
            files_obj = dict((k, {}) for k in col_file[1:])
            rows_list = list(desc_data.row_values(i) for i in range(1, desc_data.nrows))
            desc_obj = create_desc_obj(files_obj, rows_list)

        if swagger_data:
            for swagger_row in range(1, swagger_data.nrows):
                entry_data_obj = dict(zip(swagger_data.row_values(0), swagger_data.row_values(swagger_row)))
                if is_new_request(entry_data_obj):
                    check_and_create_entry_yaml(entry_data_obj)
                    update_sheet_status(file_name, 'swagger', swagger_row + 1,
                                        swagger_data.row_values(0).index('status'))
        for row in range(1, sheet_data.nrows):
            data_obj = dict(zip(sheet_data.row_values(0), sheet_data.row_values(row)))
            if is_new_request(data_obj):
                yaml_str = create_data_string(data_obj)
                check_and_create_folder('/'.join(data_obj.get('fileName').split("/")[:-1]))
                yaml_file = open('{}.yaml'.format(data_obj.get('fileName')), 'w+')
                yaml_file.write(yaml_str)
                yaml_file.close()
                update_sheet_status(file_name, 'data', row + 1, sheet_data.row_values(0).index('status'))
        LOGGER.info('Files successfully created')
    else:
        LOGGER.warning('No file found at - {0}'.format(file_name))


def create_data_from_google_sheet(swagger_data, sheet_data):
    if swagger_data:
        itr = 2
        for swagger_row in swagger_data[1:]:
            entry_data_obj = dict(zip(swagger_data[0], swagger_row))
            if is_new_request(entry_data_obj):
                check_and_create_entry_yaml(entry_data_obj)
                update_google_sheet_status(SWAGGER_SPREADSHEET_ID, 'swagger!G{0}'.format(itr), sheet)
            itr += 1
    itr = 2
    for row in sheet_data[1:]:
        data_obj = dict(zip(sheet_data[0], row))
        if is_new_request(data_obj):
            yaml_str = create_data_string(data_obj)
            check_and_create_folder('/'.join(data_obj.get('fileName').split("/")[:-1]))
            yaml_file = open('{}.yaml'.format(data_obj.get('fileName')), 'w+')
            yaml_file.write(yaml_str)
            yaml_file.close()
            update_google_sheet_status(SWAGGER_SPREADSHEET_ID, 'data!L{0}'.format(itr), sheet)
        itr += 1
    return


def create_paths_using_csv(file_name):
    """function to read data from csv"""
    if path.exists(file_name):
        with open(file_name) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    columns_name = row
                    line_count = line_count + 1
                else:
                    columns_value = row
                    data_obj = dict(zip(columns_name, columns_value))
                    yaml_str = create_data_string(data_obj)
                    check_and_create_folder('/'.join(data_obj.get('fileName').split("/")[:-1]))
                    yaml_file = open('{}.yaml'.format(data_obj.get('FileName')), 'w+')
                    yaml_file.write(yaml_str)
                    yaml_file.close()
        return 1
    else:
        LOGGER.warning('No file found at - ', file_name)


def create_entry_yaml(data_obj):
    """function to create a new swagger file"""
    info = create_info_details(json.loads(data_obj.get('info')))
    tags = create_tags(json.loads(data_obj.get('tags')), desc_obj.get('swagger', {}))
    paths = create_paths(json.loads(data_obj.get('paths')))
    description = desc_obj.get('swagger', {}).get('heading', DESCRIPTION_TEXT)
    indented_desc = indent_description(description, 2)
    yaml_str = SWAGGER_STR.format(
        swagger=data_obj.get('swagger version'),
        info=info,
        schemes=data_obj.get('schemes'),
        host=data_obj.get('host'),
        tags=tags,
        paths=paths,
        description=indented_desc,
        url=json.loads(data_obj.get('info'))['url']
    )
    return yaml_str


def check_and_create_entry_yaml(entry_data_obj):
    """function to check the swagger file exist or not and create accordingly"""
    if not path.exists('swagger.yaml'):
        yaml_str = create_entry_yaml(entry_data_obj)
        yaml_file = open('swagger.yaml', 'w+')
        try:
            yaml_file.write(yaml_str)
        except:
            yaml_file.write(yaml_str.encode('utf-8'))
        yaml_file.close()
    else:
        yaml_str_tags = create_tags(json.loads(entry_data_obj.get('tags')), desc_obj.get('swagger'))
        yaml_str_paths = create_paths(json.loads(entry_data_obj.get('paths')))
        file = open('swagger.yaml', 'r+')
        contents = file.readlines()
        file.close()
        contents.insert(contents.index('paths:\n') - 1, yaml_str_tags)
        contents.append(yaml_str_paths)
        file = open("swagger.yaml", "w")
        file.writelines(contents)
        file.close()


def create_data_string(data_obj):
    """function to create parent outer skeleton of yaml"""
    file_name = data_obj.get('fileName')
    param_type = data_obj.get('paramType')
    required = data_obj.get('required')
    if data_obj.get('reqType') in ['get', 'delete']:
        req_body = create_request_params_get(json.loads(data_obj.get('parameters')), param_type, 2,
                                             desc_obj.get(file_name, {}))
    else:
        req_body = create_request_params_post(json.loads(data_obj.get('parameters')), file_name, param_type, required,
                                              desc_obj.get(file_name, {}))
    error_codes = create_error_responses(json.loads(data_obj.get('errorCodes')))
    success_response = parse_success_response(json.loads(data_obj.get('success')), 2, desc_obj.get(file_name, {}))
    yaml_str = DATA_YAML_STR.format(
        reqType=data_obj.get('reqType'),
        tags=data_obj.get('tags'),
        summary=data_obj.get('summary'),
        description=indent_description(data_obj.get('description'), 2),
        consumes=data_obj.get('consumes'),
        req_body=req_body,
        error_codes=error_codes,
        success=success_response
    )
    return yaml_str


def parse_google_sheet(sheet_id):
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    # The ID and range of a sample spreadsheet.
    # SWAGGER_SPREADSHEET_ID_ID = '1wAtcSzMA7T2-4AkP9AVc-tXJVbDxzUU62xWzZayxhGs'
    global SWAGGER_SPREADSHEET_ID
    SWAGGER_SPREADSHEET_ID = sheet_id
    SWAGGER_SHEET = 'swagger!A:G'
    DATA_SHEET = 'data!A:L'
    DESC_SHEET = 'description!A:D'

    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'config/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    global sheet
    sheet = service.spreadsheets()
    try:
        result = sheet.values().get(spreadsheetId=SWAGGER_SPREADSHEET_ID, range=SWAGGER_SHEET).execute()
        swagger_data = result.get('values', [])
    except:
        swagger_data = []
    try:
        result = sheet.values().get(spreadsheetId=SWAGGER_SPREADSHEET_ID, range=DATA_SHEET).execute()
        data = result.get('values', [])
    except:
        data = []
    try:
        result = sheet.values().get(spreadsheetId=SWAGGER_SPREADSHEET_ID, range=DESC_SHEET).execute()
        desc_data = result.get('values', [])
        col_file = [desc[0] for desc in desc_data[1:]]
        files_obj = dict((k, {}) for k in col_file[1:])
        rows_list = desc_data[1:]
        global desc_obj
        desc_obj = create_desc_obj(files_obj, rows_list)
    except:
        pass
    try:
        create_data_from_google_sheet(swagger_data, data)
        LOGGER.info('Files successfully created')
    except:
        LOGGER.warning('Failed to create docs. Please check data and try again.')
    return


if __name__ == "__main__":
    args = sys.argv[1:]
    if not len(args):
        LOGGER.error('Please enter file name and file type')
    else:
        if args[0] == '-h':
            print('To run this utility use command - python3 create_swagger.py file_format=excel file_name=<FILE_NAME>')
        else:
            params = dict(map(lambda x: x.split('='), args))
            if params.get('file_format', '').lower() == 'excel':
                if params.get('file_name'):
                    file_extension = params.get('file_name').split('.')[-1]
                    if file_extension in ['xlsx', 'xls']:
                        create_paths_by_excel(params.get('file_name'))
                    else:
                        LOGGER.error('Unsupported file format')
                else:
                    LOGGER.error('Mandatory file_name parameter is missing')
            elif params.get('file_format', '').lower() == 'google_sheet':
                if params.get('sheet_id'):
                    parse_google_sheet(params.get('sheet_id'))
                else:
                    sheet_id = json.loads(open('config/swagger_config.json').read()).get('sheet_id')
                    if sheet_id != '' and sheet_id != '<GOOGLE_SHEET_ID>':
                        parse_google_sheet(params.get('sheet_id'))
                    else:
                        LOGGER.error('No sheet id found in swagger_config as well as in command parameter')
            else:
                LOGGER.error('Unsupported input type')
