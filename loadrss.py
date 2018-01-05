import os
import glob
import shutil
from xml.dom.minidom import parse, parseString
from collections import namedtuple
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
Log = r"C:\Users\sachin\Desktop\xmlwatcher\Log"  # maintains log file here
if not os.path.exists(Log):
    os.mkdir(Log)

# add the handler to stream
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create a file handler
file_handler = logging.FileHandler(os.path.join(Log, datetime.now().strftime('log_file_%Y_%m_%d.log')))
file_handler.setLevel(logging.DEBUG)

# create a logging format
formatter = logging.Formatter('%(asctime)s: %(name)s: %(levelname)s: %(message)s')
file_handler.setFormatter(formatter)
ch.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(ch)


class XML:

    path = r'C:\Users\Sachin\Desktop\xmlwatcher'
    if not os.path.exists(path):
        os.mkdir(path)

    Archive = r'C:\Users\Sachin\Desktop\xmlwatcher\Archive'
    Error = r'C:\Users\Sachin\Desktop\xmlwatcher\Error'
    Retry = r'C:\Users\Sachin\Desktop\xmlwatcher\Retry'

    try:
        def __init__(self, faxid, email, stamptime, pages, subject, serial, status):
            self.faxid = faxid
            self.email = email
            self.stmaptime = stamptime
            self.pages = pages
            self.subject = subject
            self.serial = serial
            self.status = status
    except Exception as InitError:
        logger.debug(InitError, exc_info = True)
    

    @classmethod
    def from_xml(cls):
        xmldocs= []
        for xml in glob.glob(os.path.join(XML.path, '*.xml')):
            try:
                xmldoc = parse(xml)
                faxid = xmldoc.getElementsByTagName('FaxID')[0].firstChild.data
                email = xmldoc.getElementsByTagName('BillingCode')[0].firstChild.data
                stamptime = xmldoc.getElementsByTagName('CustomCode2')[0].firstChild.data
                pages = xmldoc.getElementsByTagName('Pages')[0].firstChild.data
                subject = xmldoc.getElementsByTagName('Subject')[0].firstChild.data
                serial = xmldoc.getElementsByTagName('CustomCode1')[0].firstChild.data
                status = xmldoc.getElementsByTagName('Status')[0].firstChild.data
                xmldocs.append((faxid, email, stamptime, pages, subject, serial, status))

            except Exception as ParseError:
                logger.error(ParseError, exc_info = True)
                if ParseError:
                    shutil.move(xml, XML.Error)
        return xmldocs
 

    

   
    # def extract_values(xml_val=[]):
    #     try:   
    #         values = XML.from_xml()

    #         for element in values:
    #             faxid = element.getElementsByTagName('FaxID')[0].firstChild.data
    #             email = element.getElementsByTagName('BillingCode')[0].firstChild.data
    #             stamptime = element.getElementsByTagName('CustomCode2')[0].firstChild.data
    #             pages = element.getElementsByTagName('Pages')[0].firstChild.data
    #             subject = element.getElementsByTagName('Subject')[0].firstChild.data
    #             serial = element.getElementsByTagName('CustomCode1')[0].firstChild.data
    #             status = element.getElementsByTagName('Status')[0].firstChild.data
    #             xml_val.append((faxid, email, stamptime, pages, subject, serial, status))
    #     except Exception as ParseError:
    #         logger.error(ParseError)
    #     return xml_val

    @staticmethod
    def tup_data():
        data_fields=[]
        try:
            x = XML.from_xml()
            data = namedtuple('data', ['faxid', 'email', 'stamptime', 'pages', 'subject', 'serial', 'status'])
            for v in x:
                faxid =     v[0]
                email =     v[1]
                stamptime = v[2]
                pages =     v[3]
                subject =   v[4]
                serial =    v[5]
                status =    v[6]
                # sub = data('12', 'sachin@rinconc.com', '12-sep', '2', 'Test', '000001', 'DoneoK')
                s = data(faxid, email, stamptime, pages, subject, serial, status)
                data_fields.append(s)
        except Exception as f:
            logger.error(f, exc_info=True)
        return data_fields

    @classmethod
    def send_response(cls):
        try:
            f = XML.tup_data()
            for data_f in f:
                logger.info("FaxID : {}".format(data_f.faxid))
                logger.info("Email ID : {}".format(data_f.email))
                logger.info("Stamp Time : {}".format(data_f.stamptime))
                logger.info("Pages Count : {}".format(data_f.pages))
                logger.info("Subject : {}".format(data_f.subject))
                logger.info("Serial Number : {}".format(data_f.serial))
                logger.info("Status : {}".format(data_f.status))
                cc_list = ['sachinksalve90@outlook.com', 'sachinsalve90@outlook.com']
                email_user = ''
                email_password = ''
                email_send = data_f.email
        

                msg = MIMEMultipart()
                msg['From'] = email_user
                msg['CC'] = ', '.join(cc_list)
                msg['To'] = email_send
                msg['Subject'] = data_f.subject

                body = """Thank you writing to us.

Kindly take care of the following aspects:

1.   For processing the request, all the mandatory debugrmation and signature(s) are required.
2.   Processing confirmation / rejection will be intimated in due course of time.
3.   This facility is only for existing investors.
4.   Request should be received from registered email ID.

If you require any further debugrmation, our Investor Help Lines are available to assist you at Non-Toll Free No. 022-6748 3333

We look forward to a long term association and would like to assure you the best of our services.

Yours truly,\n\nUnion Mutual Fund"""

                msg.attach(MIMEText(body, 'plain'))
                part = MIMEBase('application', 'octet-stream')

                text = msg.as_string()
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(email_user, email_password)
                try:
                    server.sendmail(email_user, [email_send, cc_list], text)
                except Exception as MailError:
                    logger.error(MailError, exc_info = True)
                logger.debug("email repose sent to {}".format(data_f.email, cc_list))
                server.quit()
        except Exception as ParseError:
            logger.error(ParseError, exc_info=True)
            

XML.send_response()
