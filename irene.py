import os 

import httplib2
import oauth2client
from oauth2client import client, tools, file
import base64
import email 
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apiclient import errors, discovery
import mimetypes
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase

import warnings

CREDENTIALS, SERVICE = None, None
STRICT = True
GLOBAL_SENDER = None
SCOPES = ['https://mail.google.com']
APPLICATION_NAME = 'Irene EMail Sender'


import logging
logger = logging.getLogger(__name__)


class DefaultDict(dict):
    __getitem__ = lambda self, key : self.get(key , f'{{{key}}}') 

def get_ppl_str(ppl : list):
    
    if isinstance(ppl , str):
        return ppl 
    
    elif isinstance(ppl , bytes):
        return ppl.decode('utf8')

    elif isinstance(ppl , (list , tuple, set )):
        return ', '.join(ppl)

    else:

        raise TypeError(f'Argument ppl can only be string/list/iterable, not {type(ppl).__name__}')

def get_msgId(msgId , threadId):

    global SERVICE

    msg = SERVICE.users().messages().get(userId = 'me' , id = msgId , format = 'raw').execute()
    msg = base64.urlsafe_b64decode(msg['raw']).decode('utf8')
    msg = email.message_from_string(msg)
    return msg['Message-ID']

def send_mail(  to : list  , 
                body_html_template : str  ,
                data : DefaultDict,
                cc : list = None , 
                subject : str = "",
                threadId : str = None , msgId : str = None , 
                attachment : str = None, a_type : str = 'file' ):

    global CREDENTIALS, GLOBAL_SENDER

    msg = MIMEMultipart()
    data = DefaultDict(data)

    msg['to'] = rec  = get_ppl_str(to)
    msg['from'] = GLOBAL_SENDER
    if cc is not None:
        msg['cc'] = get_ppl_str(cc)
    
    msg['subject'] = subject.format_map(data)
    body = body_html_template.format_map(data)

    if threadId is not None:

        assert isinstance(threadId , str),  f'Thread ID needs to be a string'
        assert isinstance(msgId, str),      f'Message ID needs to be a string'

        msgId = get_msgId(msgId , threadId)

        msg.add_header('Reference' , msgId)
        msg.add_header('In-Reply-To' , msgId)

    msg.attach(MIMEText(body , 'html'))

    if attachment is not None:

        add_attachments(msg , attachments, a_type)

        #msg.attach(add_attachment(attachment , a_type))


    sent = SendMailInternal(rec , msg , threadId)

    return sent

def add_attachments(msg : MIMEMultipart ,attachments , a_type = 'file'):

    if isinstance(attachments, str):

        s = add_attachment(attachments , a_type)
        
        if s is None:
            warnings.warn('Attachment skipped')
        
        return msg.attach(s)

    elif hasattr(attachments, '__iter__'):          

        _ = [ add_attachments(msg , str(attachment) , a_type) for attachment in attachments]

    else:

        raise TypeError(f'Attachments must be in string form(single) or iterable. Class {type(attachments).__name__} is invalid' ) 

def SendMailInternal(rec , msg : MIMEMultipart , threadId : str = None):

    global GLOBAL_SENDER , SERVICE

    msg = { 'raw'  : base64.urlsafe_b64encode(msg.as_bytes()).decode('utf8')}

    if threadId is not None:
        msg.update({'threadId': threadId})

    for i in range(3):

        try:
            message = SERVICE.users().messages().send(userId = 'me' , body = msg).execute()
            return message

        except:

            warnings.warn(f'Mail to {rec} failed, will try {2-i} more times')
            continue 

def add_attachment(file : str , a_type : str  = 'file' ):

    print('a adding')

    if a_type == 'url':
        import subprocess
        os.makedirs('./tmp')
        t = subprocess.call(['curl' , file , '--create-dirs' , '-O' , '--output-dir' , './tmp' ] )
        if t !=0:

            if STRICT:
                raise Exception(f"Url {file} cannot be downloaded to attach")

            else:
                warnings.warn(f'Url {file} cannot be downloaded. Returning None')
                return None

        else:

            file = os.path.join('./tmp' , list(os.listdir('./tmp'))[0]) 
    
    content_type, encoding = mimetypes.guess_type(file)

    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    
    main_type, sub_type = content_type.split('/', 1)
    
    if main_type == 'text':
        fp = open(file, 'rb')
        msg = MIMEText(fp.read(), _subtype=sub_type)
        fp.close()
    
    elif main_type == 'image':
        fp = open(file, 'rb')
        msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
    
    elif main_type == 'audio':
        fp = open(file, 'rb')
        msg = MIMEAudio(fp.read(), _subtype=sub_type)
        fp.close()
    
    else:
        fp = open(file, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()
    
    filename = os.path.basename(file)
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
        
    if a_type == 'url':
        os.remove(file)

    return msg

def nan_to_None(val):

    if val != val:
        return None

    return val

def None_to_nan(val):

    if val is None:
        return float('nan')

    return val

def get_client( client_file : str = None, token   : str = None):  

    global CREDENTIALS, SERVICE, APPLICATION_NAME , SCOPES

    if CREDENTIALS is not None:
        logger.debug("Client is already setup")
        return False 

    if (token is None) or (not os.path.exists(str(token))):
        
        if token is None:
            token = './token.json'

        with open(token , 'wb') as handle:
            pass

    store = oauth2client.file.Storage(token)
    CREDENTIALS = store.get()

    if not CREDENTIALS or CREDENTIALS.invalid:
        flow = client.flow_from_clientsecrets(client_file, SCOPES)
        flow.user_agent = APPLICATION_NAME
        CREDENTIALS = tools.run_flow(flow, store)

    http = CREDENTIALS.authorize(httplib2.Http())
    SERVICE = discovery.build('gmail', 'v1', http=http)

    return CREDENTIALS, SERVICE