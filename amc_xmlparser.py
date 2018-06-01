# Import all the required module

import bs4
import glob
import logging
import logging.handlers as handlers
import os
import shutil
import smtplib
import timeit
import time
from datetime import datetime
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from xml.dom.minidom import parse
import mailbody
import cc
import auth

start = timeit.default_timer()


def main():
    logger = logging.getLogger('XMLParsingService')
    logger.setLevel(logging.DEBUG)
    Log = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Log')  # maintains log file here  # maintains log file here
    if not os.path.exists(Log):
        os.mkdir(Log)

    # add the handler to stream
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create a file handler
    # file_handler = logging.FileHandler(os.path.join(Log, datetime.now().strftime('log_file_%Y_%m_%d.log')))

    # file_handler.setLevel(logging.DEBUG)

    logHandler = handlers.TimedRotatingFileHandler(os.path.join(Log, datetime.now().strftime('log_file_%Y_%m_%d.log')), when='midnight', backupCount=10)
    logHandler = handlers.RotatingFileHandler(os.path.join(Log, datetime.now().strftime('log_file_%Y_%m_%d.log')), maxBytes=5000000, backupCount=10)
    logHandler.setLevel(logging.DEBUG)


    # create a logging format
    formatter = logging.Formatter('%(asctime)s: [%(thread)d]:[%(name)s]: %(levelname)s:[AutoReply] - %(message)s')
    logHandler.setFormatter(formatter)
    ch.setFormatter(formatter)

    

    # add the handlers to the logger
    logger.addHandler(logHandler)
    logger.addHandler(ch)


    logger.debug("XML parsing started...")

    # base_path = os.path.dirname(os.path.realpath(__file__))
    base_path = os.path.dirname(os.path.realpath(__file__))
    logger.debug("Parsing XMLs from folder: {}".format(base_path))

    dst_path = os.path.join(base_path, 'Archive')
    if not os.path.exists(dst_path):
        os.mkdir(dst_path)

    totalxml = len(glob.glob(os.path.join(base_path, '*.xml')))
    totalxml =0
    while not totalxml:

        retry = os.path.join(base_path, 'Retry')
        if not os.path.exists(retry):
            os.mkdir(retry)

        error_path = os.path.join(base_path, 'Error')
        if not os.path.exists(error_path):
            os.mkdir(error_path)

       
        totalfailedxml = len(glob.glob(os.path.join(retry, '*.xml')))
        totalfailedxml = 0
        while not totalfailedxml:

            #checking Retry folder for the xml which were failed because of EMail Server Issues.
            logger.debug("Parsing XMLs from Retry folder..")
            # totalfailedxml = len(glob.glob(os.path.join(retry, '*.xml')))
            logger.debug("Found XMLs in Retry Folder, Count: {}".format(totalfailedxml))

            for XMLFile in glob.glob(os.path.join(retry, '*.xml')):
                shutil.move(XMLFile, base_path)
                logger.debug("Moved XMLs {} from Retry Folder to Base folder(Reprocessing)".format((XMLFile.split("\\")[-1])))
                for pdfs in glob.glob(os.path.join(retry, '*.pdf')):
                    shutil.move(pdfs, base_path)
                    logger.debug("moved XMl from retry folder to main folder %s", (pdfs.split("\\")[-1]))
            totalxml = 0
            while not totalxml:
                totalxml = len(glob.glob(os.path.join(base_path, '*.xml')))
                logger.debug("Found XMLs, count: {}".format(totalxml))
                if totalxml == 0:
                    logger.debug("No XMLs to parse")
                try:
                    for XMLFile in glob.glob(os.path.join(base_path, '*.xml')):
                        infile=open(XMLFile, 'r')
                        contents = infile.read()
                        soup = bs4.BeautifulSoup(contents, 'html.parser')
                        logger.debug("Parsing XML : {}".format(os.path.basename(XMLFile)))
                        FaxID = soup.faxid.string
                        logger.debug("Fax ID : {}".format(FaxID))
                        EmailID = faxid = soup.billingcode.string
                        logger.debug("Email id of Sender : {}".format(EmailID))
                        StampTime = faxid = soup.matter.string
                        logger.debug("Stamp Time : {}".format(StampTime))
                        Pages = faxid = soup.pages.string
                        logger.debug("Pages received : {}".format(Pages))
                        SerialNumber =faxid = soup.customcode1.string
                        logger.debug("Serial Number : {}".format(SerialNumber))
                        Status = faxid = soup.status.string
                        logger.debug("Status : {}".format(Status))
                    
                
                        try:
                            Subject = faxid = soup.fromname.string
                        except Exception:
                            logger.error(Exception, exc_info=True)
                        
                            if Exception:
                                logger.debug("No subject line received, setting up default value for subject")
                                Subject = 'Transaction Confirmation!'  
                                          
                        logger.debug("Subject : {}".format(Subject))
                        logger.debug("All fileds are extracted, submitting file {} to Mail Server".format(os.path.basename(XMLFile)))


                        try:
                            validxml = 0
                            while True:
                                cc_list = cc.ccs
                                email_user = auth.username
                                email_password = auth.password
                                email_send = EmailID
                                msg = MIMEMultipart()
                                msg['From'] = email_user
                                msg['CC'] = ', '.join(cc_list)
                                msg['To'] = email_send
                                msg['Subject'] = 'RE: '+''+Subject
                                body = mailbody.mail_string
                                msg.attach(MIMEText(body, 'plain'))
                                filename='{}.pdf'.format(FaxID)

                                
                                try:
                                    attachment  =open(filename,'rb')
                                    part = MIMEBase('application', 'octet-stream')
                                    part.set_payload((attachment).read())
                                    encoders.encode_base64(part)
                                    part.add_header('Content-Disposition',"attachment; filename= "+filename)
                                    msg.attach(part)

                                except Exception as FileNotFoundError:
                                    logger.debug("Attachment file {}.pdf not found".format(FaxID))

                                    if not os.path.exists(os.path.join(base_path, '{}.pdf'.format(FaxID))):
                                        logger.debug("Processing next XML file")
                                        break

                                    else:
                                        continue

                                text = msg.as_string()
                                server = smtplib.SMTP('smtp-mail.outlook.com', 587)
                                server.starttls()
                                server.login(email_user, email_password)
                                server.sendmail(email_user, [email_send], text)
                                try:
                                    part.set_payload((attachment).close())
                                except Exception as F:
                                    pass
                                server.quit()
                                infile.close()
                                            
                                if True:
                                    infile.close()
                                    shutil.move(XMLFile.split("\\")[-1], dst_path)
                                    shutil.move('{}.pdf'.format(FaxID), dst_path)
                                    logger.debug("XML %s is moved to Folder %s",
                                                 (XMLFile.split("\\")[-1]), (dst_path))

                                    logger.debug("XMLs process and sent to Destinations 'TO' : {}, 'CC': {}".format(email_send, cc_list))
                                    logger.debug("Processing next XML file")

                                else:
                                    infile.close()
                                    shutil.move(XMLFile.split("\\")[-1], retry)
                                    shutil.move('{}.pdf'.format(FaxID), retry)
                                    validxml += 1
                                break


                        except Exception as SendMailError:
                            infile.close()
                            logger.error(SendMailError, exc_info=True)
                            logger.debug("Error occured while sending an email...")
                            part.set_payload((attachment).close())
                            shutil.move(XMLFile.split("\\")[-1], retry)
                            shutil.move('{}.pdf'.format(FaxID), retry)
                            logger.debug("Processing next XML file")


                except Exception as error:
                    infile.close()
                    shutil.move(XMLFile.split("\\")[-1], error_path)
                    try:
                        shutil.move('{}.pdf'.format(XMLFile.split("\\")[-1].split(".")[0]), error_path)
                    except Exception as FileNotFoundError:
                        pass
                    logger.error(error, exc_info=True)
                    logger.debug("some attributes from XML file %s are missing, moving file to Error directory %s",
                                 (XMLFile.split("\\")[-1]), (error_path))
                    logger.debug("Processing next XML file")
                    logger.debug("XML parsing finished.")
                   
                else:
                    logger.info("thread sleep for 5 second(s)")
                    time.sleep(5)

                    break

            continue

        continue  
           
main()

stop = timeit.default_timer()

print("Time taken for execution : {:2f} seconds".format((stop - start)))
# !/usr/bin/env
