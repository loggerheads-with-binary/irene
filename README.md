
# Irene: 
## A simple wrapper around the GMail API without the unncessary complexity sorrounding it 

### Introduction:

This project was specifically build to cater the need of replying to mail threads in a smooth and efficient manner. This script exposes the very few key functions required to actually build a workable model for such mail threads. The

The primary use case can be chalked down to mail campaigns where they wish subsequent mails to be delivered through the same thread. 

It has been adequately tested, however any breaks/bugs can be reported


### Installation of  the project:

This project can be used through the use of jupyter notebooks or using python scripts.

**For colab/ipynb, add the following lines before importing the script** 
```
import sys 
! {sys.executable} -m pip install google_api_python_client google_auth_oauthlib httplib2 oauth2client protobuf
```

**For python installations, consider building a virtual environment**
```
python3 -m pip install virtualenv
python3 -m venv . gmail_venv
activate 
curl "" --output requirements.txt
python3 -m pip install -r requirements.txt
```

**For anaconda installations, consider building a virtual environment this way**
```
conda create -n gmail_venv
conda activate gmail_venv
curl "" --output requirements.txt
python3 -m pip install -r requirements.txt
```

**Copy the main script to your *(For python/anaconda installations)* machine**
```
curl "" --output irene.py
```

**Copy the main script to *(Jupyter/Colab)*  your locale**
```
!curl ""
```

## Generating a token:

From google console, create a new OAuth2 ID and download the file as `client.json`
Create a blank new file called `token.json`

Run this code on your system:
```
import irene
irene.get_client('client.json' , 'token.json')
```
It should open your default web browser and ask you to sign in with the google credentials of your preferred EMail.
**Note:: This EMail ID must be the one you wish to send mails from**. **

Also, after the login, the script could crash as observed a few times. This is okay as the token file has been generated.

In the downloaded `irene.py` script, also modify the variable `GLOBAL_SENDER` to whatever Google Mail you have logged in from.


### Using the project:

Make appropriate modifications to the below test case 

```
##Client setup
import irene
irene.get_client(token =  'token.json' )


import pandas as pd
import numpy as np  
df = pd.read_csv('data.csv')            ##Make sure columns count, threadId, msgId exist in the CSV, even if they are filled blank

BODY_TEXT = """\
Hello {name},

Hope you are having a good day.

Please find your billing token {token_billing} attached for the shipment to {cust_address}

Regards,
John Smith and Jade Smith Inc.
+0 123 456 7890
"""

df['count'] = df['count'].fillna(0)     ##Assigns a value of 0 for any rows with count being blank

for _idx , row in df.iterrows():

    

    msgId = irene.nan_to_None(row['msgId'])         ##nan_to_None is a safety function
    threadId = irene.nan_to_None(row['threadId'])

    response = irene.send_mail( to = "sample@example.com" , body_html_template = BODY_TEXT , #to and body_html_template are compulsory arguments
                                data = row,             ##Compulsory, just send dict() if you have fixed body text and subject with no variables
                                cc = ['1@2.com' , '33@23andme.com' ] , subject = 'Well well well' ,     ##cc and subject are not mandatory
                                msgId = msgId, threadId = threadId , 
                                attachment = None,  ##attach a file/url
                                a_type = None       ##Use 'file' if attachment is a file, else 'url' if it is a URL
    )   

    row['count'] +=1 
    row['msgId' ]  = response['id']
    row['threadId'] = response['threadId']

df.to_csv('data.csv')   ##Saving the dataframe for next use
````                            
