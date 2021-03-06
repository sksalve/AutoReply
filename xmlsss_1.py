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
import csv
start = timeit.default_timer()

def main():
    logger = logging.getLogger('xmlParseService')
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

    logger.debug("XML fetching process started......")

    # base_path = os.path.dirname(os.path.realpath(__file__))
    base_path = r'C:\Users\sachin\Desktop\xmlwatcher'
    logger.debug("Current path to fetch XMLS........%s", base_path)

    dst_path = r"C:\Users\sachin\Desktop\xmlwatcher\Archive"
    if not os.path.exists(dst_path):
        os.mkdir(dst_path)

    totalxml = len(glob.glob(os.path.join(base_path, '*.xml')))
    logger.debug("XMLs fetched from directory, count is...:%s", totalxml)
    if totalxml == 0:
        logger.debug("There are no new XMLs to process....")

    retry = r"C:\Users\sachin\Desktop\xmlwatcher\Retry"
    if not os.path.exists(retry):
        os.mkdir(retry)

    error_path = r"C:\Users\sachin\Desktop\xmlwatcher\Error"
    if not os.path.exists(error_path):
        os.mkdir(error_path)

    # Check Retry folder before proceeding further...

    logger.debug("Checking Retry folder for any failed XMLs due to mail server/credentials issues...")
    totalfailedxml = len(glob.glob(os.path.join(retry, '*.xml')))
    logger.debug("total XMls found in retry folder, count is :%s", totalfailedxml)

    totalfailedxml = 0
    while not totalfailedxml:

        for XMLFile in glob.glob(os.path.join(retry, '*.xml')):
            shutil.move(XMLFile, base_path)
            logger.debug("moved XMl from retry folder to main folder %s", (XMLFile.split("\\")[-1]))

        totalxml = 0
        while not totalxml:
            try:
                for XMLFile in glob.glob(os.path.join(base_path, '*.xml')):
                    xmldoc = parse(XMLFile)
                    logger.debug("Processing XML file %s", XMLFile.split("\\")[-1])
                    FaxID = xmldoc.getElementsByTagName('FaxID')[0].firstChild.data
                    logger.debug("Getting attribute 'ReferenceNumber' from XML, the value of the field is %s", FaxID)
                    EmailID = xmldoc.getElementsByTagName('BillingCode')[0].firstChild.data
                    logger.debug("Getting attribute  'Email Id of Sender' from XML, the value of the field is %s", EmailID)
                    StampTime = xmldoc.getElementsByTagName('CustomCode2')[0].firstChild.data
                    logger.debug("Getting attribute  'Stamp Time' from XML, the value of the field is %s", StampTime)
                    Pages = xmldoc.getElementsByTagName('Pages')[0].firstChild.data
                    logger.debug("Getting attribute 'Pages' from XML, the value of the field is %s", Pages)
                    SerialNumber = xmldoc.getElementsByTagName('CustomCode1')[0].firstChild.data
                    logger.debug("Getting attribute 'SerialNumber' from XML, the value of the field is %s", SerialNumber)
                    Status = xmldoc.getElementsByTagName('Status')[0].firstChild.data
                    logger.debug("Getting attribute 'Status' from XML, the value of the field is %s", Status)
                    try:
                        Subject = xmldoc.getElementsByTagName('Matter')[0].firstChild.data
                    except Exception:
                        logger.debug(Exception)
                        if Exception:
                            Subject = 'Transaction Confirmation!'             
                    logger.debug("Getting attribute 'Subject' from XML, the value of the field is %s", Subject)
                    logger.debug("Submitting request to mail server for XML attribute with name %s",XMLFile.split("\\")[-1])
                   
                    try:
                        validxml = 0
                        while True:
                       
                            cc_list = ['sachins@rincon.co.in']
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

                            server.sendmail(email_user, [email_send, cc_list], text)
                            server.quit()

                            if True:
                                shutil.move(XMLFile.split("\\")[-1], (dst_path, Archive))
                                logger.debug("Xml file %s has been successfully moved to location %s",
                                             (XMLFile.split("\\")[-1]), (dst_path))
                                logger.debug("Xml file %s has been successfully processed and sent to destination :%s",
                                             (XMLFile.split("\\")[-1]), ("TO : {}, CC: {}".format(email_send, cc_list)))
                                logger.debug("Processing next XML file")

                            else:
                                shutil.move(XMLFile.split("\\")[-1], retry)
                                validxml += 1
                            break

                    except Exception as SendMailError:
                        logger.debug(SendMailError, exc_info=True)
                        logger.debug("Some issues with sending email...")
                        shutil.move(XMLFile.split("\\")[-1], retry)
                        logger.debug("Processing next XML file")

            except Exception as error:
                shutil.move(XMLFile.split("\\")[-1], error_path)
                logger.debug(error, exc_info=True)
                logger.debug("some attributes from XML file %s is missing, moving file to Error directory %s",
                             (XMLFile.split("\\")[-1]), (error_path))
                logger.debug("Processing next XML file")
                logger.debug("XML fetching finished...... process will start after 5 minutes.")
            else:
                logger.info("sleeping for next 25 second(s)")
                time.sleep(25)
                break
        continue


main()




stop = timeit.default_timer()

print("Time taken for execution : {:2f} seconds".format((stop - start)))
# !/usr/bin/env
