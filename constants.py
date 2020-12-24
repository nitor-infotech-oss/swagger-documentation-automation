"""
This file contains all the constant values which we need to use within all project files.
"""

TWO_SPACES = '  '
FOUR_SPACES = '    '
DESCRIPTION_TEXT = 'Add description here'
PATH_TEXT = 'Add file path here'
DICTIONARY_DATA_TYPE = {'dict': 'object', 'list': 'array', 'str': 'string', 'int': 'integer',
                        'bool': 'boolean', 'unicode': 'string', 'float': 'float'}

SWAGGER_STR = u'''swagger: {swagger}
info:
{info}
  x-logo:
    url: {url}  
  description: |
    {description}  
schemes:
  - {schemes}
host:
  - {host}
tags:
{tags}
paths:
{paths}
'''

DATA_YAML_STR = '''{reqType}:
  tags:
    - {tags}
  summary: {summary}
  description: | 
    {description}
  consumes:
    - {consumes}
  parameters:
{req_body}
  responses: {success}
{error_codes}
'''

SUCCESS_STR = '''    
    {0}:
      description: Success Response
      content:
        application/json:
          schema:
{1}'''

INNER_PARAM_STR = '''{4}{0}:
{4}  type: {1}
{4}  example: {2}
{4}  enum: 
{4}  format: 
{4}  description: |  
{4}    {3}
'''


OBJECT_STR = '''{0}{3}:
{0}  type: {1}
{0}  description: |  
{0}    {4}
{0}  properties: 
{2}
'''