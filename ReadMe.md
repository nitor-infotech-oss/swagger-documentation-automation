# Swagger Document Automation in Python

This is a python based utility which will help stakeholders such as technical writers, BA, developers to create a software document by using excel or google sheet. 
This utility saves the stakeholder time by creating multiple yaml doc files from the provided inputs(excel/google sheet).
 
 
### Tools & Technology

1. Python
2. YAML
3. Redoc


### Pre-requisite

1. Python 3
2. pip (Python package installer)
3. Google Sheet Support (Refer Google sheet support section below)


### Steps to run swagger file

1. Install python3
        
        https://www.python.org/downloads/

2. Install required packages:

        Open terminal for (Linux/mac) or cmd for windows and run the following commands: 

        pip install xlrd 
        pip install openpyxl 
        pip install google-api-core==1.21.0
        pip install google-api-python-client==1.9.3
        pip install google-auth==1.18.0
        pip install google-auth-httplib2==0.0.3
        pip install google-auth-oauthlib==0.4.1
        pip install googleapis-common-protos==1.52.0


3. Browse to folder - SwaggerDoc in your terminal / cmd

4. Google Sheet Configuration:
        
        If you are using google sheet, then go to the below link: 
            [Click Here]: https://developers.google.com/sheets/api/quickstart/python 
        Enable google sheet api for your sheet and download the "creadentails.json" file.
        
        Replace the client_id and client_secret with your credentials or replace "credentials.json" with yours file in main folder.
        Add "GOOGLE_SHEET_ID" into swagger_config.json file.
        
5. Run command: 
        
    This utility supports excel and google sheets as an input.         
        
      ##### If the user want to create the docs from excel then for excel the command is given below:
        
            python3 create_swagger.py file_format=excel file_name=<FILE_NAME>
            
      ###### For excel both the extension are supported ie. xls, xlsx    
        
      #####  If the user want to create the docs using google sheet then for that the command is given below:
        
            python3 create_swagger.py file_format=google_sheet sheet_id=<GOOGLE_SHEET_ID>
           
      #####  If user dont want to provide sheet id every time then it can be configured in swagger_config.json. In that case the command will be: 
            
            python3 create_swagger.py file_format=google_sheet
                
6. Once the files are created. Open **index.html** in any browser to view the created document.

### Note:

1. For Best practice paste your excel in the same folder - SwaggerDoc
2. Execution Logs are generated dynamically under logs folder
3. To update existing file or to create a new file, there is a column in Excel sheet `status` as given in the Excel 
   template. Set the value to `new` for any new creation or update. Once the file gets created it will change to `published` 
   automatically by the utility.
4. A template excel is present in the project name - `SwaggerDataSheet.xlsx`. This format is same for google sheets as well.
