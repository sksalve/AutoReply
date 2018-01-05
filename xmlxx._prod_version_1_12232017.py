# Import all the required modules here!

import glob
import logging
import os
import shutil
import smtplib
import timeit
import time
from datetime import datetime
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from xml.dom.minidom import parse


start = timeit.default_timer()


def main():
    logger = logging.getLogger('XMLParsingService')
    logger.setLevel(logging.DEBUG)
    Log = r"C:\Users\sachins\Desktop\xmlwatcher\Log"  # maintains log file here
    if not os.path.exists(Log):
        os.mkdir(Log)

    # add the handler to stream
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create a file handler
    file_handler = logging.FileHandler(os.path.join(Log, datetime.now().strftime('log_file_%Y_%m_%d.log')))
    file_handler.setLevel(logging.DEBUG)

    # create a logging format
    formatter = logging.Formatter('%(asctime)s: %(name)s: %(levelname)s: %(processName)s:%(thread)d(AutoReply):%(message)s')
    file_handler.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(ch)

    logger.debug("XML parsing started...")

    # base_path = os.path.dirname(os.path.realpath(__file__))
    base_path = r'C:\Users\sachins\Desktop\xmlwatcher'
    logger.debug("Parsing XMLs from folder: {}".format(base_path))

    dst_path = r"C:\Users\sachins\Desktop\xmlwatcher\Archive"
    if not os.path.exists(dst_path):
        os.mkdir(dst_path)

    totalxml = len(glob.glob(os.path.join(base_path, '*.xml')))
    totalxml =0
    while not totalxml:
        # logger.debug("Found XMLs, count: {}".format(totalxml))
        # if totalxml == 0:
        #     logger.debug("No XMLs to parse")

        retry = r"C:\Users\sachins\Desktop\xmlwatcher\Retry"
        if not os.path.exists(retry):
            os.mkdir(retry)

        error_path = r"C:\Users\sachins\Desktop\xmlwatcher\Error"
        if not os.path.exists(error_path):
            os.mkdir(error_path)

        

        totalfailedxml = 0
        while not totalfailedxml:

            #checking Retry folder for the xml which were failed because of EMail Server Issues.
            logger.debug("Parsing XMLs from Retry folder..")
            totalfailedxml = len(glob.glob(os.path.join(retry, '*.xml')))
            logger.debug("Found XMLs in Retry Folder, Count: {}".format(totalfailedxml))

            for XMLFile in glob.glob(os.path.join(retry, '*.xml')):
                shutil.move(XMLFile, base_path)
                logger.debug("Moved XMLs {} from Retry Folder to Base folder(Reprocessing)".format((XMLFile.split("\\")[-1])))

            totalxml = 0
            while not totalxml:
                totalxml = len(glob.glob(os.path.join(base_path, '*.xml')))
                logger.debug("Found XMLs, count: {}".format(totalxml))

                if totalxml == 0:
                    logger.debug("No XMLs to parse")
                try:
                    for XMLFile in glob.glob(os.path.join(base_path, '*.xml')):
                       
                        xmldoc = parse(XMLFile)
                        logger.debug("Parsing XML : {}".format(XMLFile.split("\\")[-1]))
                        
                        FaxID = xmldoc.getElementsByTagName('FaxID')[0].firstChild.data
                        
                        logger.debug("Fax ID : {}".format(FaxID))
                        
                        EmailID = xmldoc.getElementsByTagName('BillingCode')[0].firstChild.data
                        
                        logger.debug("Email id of Sender : {}".format(EmailID))
                        
                        StampTime = xmldoc.getElementsByTagName('Matter')[0].firstChild.data
                        
                        logger.debug("Stamp Time : {}".format(StampTime))
                        
                        Pages = xmldoc.getElementsByTagName('Pages')[0].firstChild.data
                        
                        logger.debug("Pages received : {}".format(Pages))
                        
                        SerialNumber = xmldoc.getElementsByTagName('CustomCode1')[0].firstChild.data
                        
                        logger.debug("Serial Number : {}".format(SerialNumber))
                        
                        Status = xmldoc.getElementsByTagName('Status')[0].firstChild.data
                        
                        logger.debug("Status : {}".format(Status))
                        
                        try:
                            Subject = xmldoc.getElementsByTagName('FromName')[0].firstChild.data
                        except Exception:
                            logger.debug(Exception, exc_info=True)
                            
                            if Exception:
                                logger.debug("No subject line received, setting up default value for subject")
                                Subject = 'Transaction Confirmation!'              
                        logger.debug("Subject : {}".format(Subject))
                        
                        logger.debug("All fileds are extracted, submitting to Mail Server %s",XMLFile.split("\\")[-1])
                        
                        try:
                            validxml = 0
                            while True:
                            
                                cc_list = ['sachins@rincon.co.in', 'sachinksalve90@gmail.com']
                                email_user = ''
                                email_password = ''
                                email_send = EmailID

                                msg = MIMEMultipart()
                                msg['From'] = email_user
                                msg['CC'] = ', '.join(cc_list)
                                msg['To'] = email_send
                                msg['Subject'] = Subject

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

                                server.sendmail(email_user, [email_send], text)
                                server.quit()

                                if True:
                                    shutil.move(XMLFile.split("\\")[-1], dst_path)
                                    logger.debug("XML %s is moved to Folder %s",
                                                 (XMLFile.split("\\")[-1]), (dst_path))
                                    # logger.debug("XML %s is successfully processed and sent to destination :%s",
                                    #              (XMLFile.split("\\")[-1]), (email_send, cc_list))
                                    logger.debug("XMLs process and sent to Destinations 'TO' : {}, 'CC': {}".format(email_send, cc_list))
                                    logger.debug("Processing next XML file")

                                else:
                                    shutil.move(XMLFile.split("\\")[-1], retry)
                                    validxml += 1
                                break

                        except Exception as SendMailError:
                            logger.debug(SendMailError, exc_info=True)
                            logger.debug("Error occured while sending an email...")
                            shutil.move(XMLFile.split("\\")[-1], retry)
                            logger.debug("Processing next XML file")


                except Exception as error:
                    shutil.move(XMLFile.split("\\")[-1], error_path)
                    logger.debug(error, exc_info=True)
                    logger.debug("some attributes from XML file %s are missing, moving file to Error directory %s",
                                 (XMLFile.split("\\")[-1]), (error_path))

                    if totalfailedxml!=0:
                        logger.debug("Processing next XML file")
                    logger.debug("XML parsing finished.")
                else:
                    
                    logger.info("thread sleep for 15 second(s)")
                    time.sleep(25)

                    break
                
            continue
        continue   
            
main()

stop = timeit.default_timer()

print("Time taken for execution : {:2f} seconds".format((stop - start)))
# !/usr/bin/env
