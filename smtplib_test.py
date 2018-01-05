import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# from email.mime.Multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

FaxID= 255
StampTime = '25Nov2017 12:45'
EmailID = 'sachin.salve87@gmail.com'

email_user = ''
email_password = ''
email_send = EmailID

subject = 'Transaction Confirmation'
cc_list = ['sachinksalve90@gmail.com', 'sachins@rincon.co.in']
bcc_list = ''


msg = MIMEMultipart()
msg['From'] = email_user
msg['Cc'] = ';'.join(cc_list)
msg['Bcc'] = '; '.join(bcc_list)
msg['To'] = email_send
 
msg['Subject'] = subject

body = "Thank you writing to us.\n\nYour reference Id is: " + str(FaxID) + "\n\n" + "The stamped time is :" + str(StampTime) + "\n\n" + "Kindly take care of the following aspects:\n\n" "1\tFor processing the request, all the mandatory debugrmation and signature(s) are required.\n""2.\tProcessing confirmation / rejection will be intimated in due course of time.\n""3.\tThis facility is only for existing investors.\n""4.\tRequest should be received from registered email ID.\n\n""If you require any further debugrmation, our Investor Help Lines are available to assist you at Non-Toll Free No. 022-6748 3333.\n\n""We look forward to a long term association and would like to assure you the best of our services.\n\n""Yours truly,\n\n""Union Mutual Fund"
msg.attach(MIMEText(body,'plain'))
##
##filename='filename'
##attachment  =open(filename,'rb')

part = MIMEBase('application','octet-stream')
##part.set_payload((attachment).read())
##encoders.encode_base64(part)
##part.add_header('Content-Disposition',"attachment; filename= "+filename)

##msg.attach(part)
text = msg.as_string()
server = smtplib.SMTP('smtp-mail.outlook.com',587)
server.starttls()
server.login(email_user,email_password)

print("email procedure completed SUCCESS/ERROR")


server.sendmail(email_user,[email_send], text)
# server.sendmail(email_user,email_send,  text)
server.quit()
