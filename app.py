# -*- coding: utf-8 -*-
import os
import smtplib
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail,Message
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import base64


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = '123456'
db = SQLAlchemy(app)



class TODO(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120),nullable=False)
    mobliePhone = db.Column(db.Integer)
    date_created = db.Column(db.DateTime,default=datetime.utcnow)

    def  __repr__(self):
        return '<Contact %r>' % self.id

@app.route('/',methods=['POST','GET'])
def index():
    if request.method == 'POST':
        new_name = request.form['username']
        new_email = request.form['email']
        new_mobliePhone = request.form['phone']
        new_contact = TODO(name=new_name,email=new_email,mobliePhone=new_mobliePhone)

        try:
            db.session.add(new_contact)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your contact'

    else:
        contacts = TODO.query.order_by(TODO.date_created).all()
        return render_template('index.html',contacts = contacts)

@app.route("/delete/<int:id>")
def delete(id):
    contact_to_delete = TODO.query.get_or_404(id)
    
    try:
        db.session.delete(contact_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return "There was an issue deleting your contact"

@app.route("/update/<int:id>" , methods=['GET','POST'])
def update(id):
    contact = TODO.query.get_or_404(id)
    

    if request.method == 'POST':
        contact.name = request.form['username']
        contact.email = request.form['email']
        contact.mobliePhone = request.form['phone']
        
        try:
            db.session.commit()
            return redirect('/')

        except:
            return 'There was an issue updating contact'
    else:
        return render_template('update.html',contact = contact)

# app.config.update(
#     MAIL_SERVER='smtp.gmail.com',
#     MAIL_PROT=587,
#     MAIL_USE_TLS= True,
#     MAIL_USE_SSL=False,
#     MAIL_DEFAULT_SENDER=('admin', '@example.com'),
#     MAIL_USERNAME='@example.com',
#     MAIL_PASSWORD='password',
#     MAIL_ASCII_ATTACHMENTS=True
# )
# mail = Mail(app)

UPLOAD_FOLDER = 'static/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/sendMail/<int:id>",methods=['GET','POST'])
def sendMail(id):
    contact = TODO.query.get_or_404(id)
    emails = TODO.query.all()
    msg=MIMEMultipart()
    
    if request.method == 'POST':
        sender = 'joanne@dcard.cc'
        msg['From'] = sender
        recipients_options = request.values.getlist('recipient')
        recipients = recipients_options
        msg['To'] =  ';'.join(recipients)
        msg['Subject'] = request.form['subject']
        body = request.form['body']
        msg.attach(MIMEText(body, _subtype='html', _charset='UTF-8'))
        files = request.files.getlist('upload_file')
        if ('application/octet-stream') not in str(files)  :
            for file in files:
                file.save(os.path.join(app.config['UPLOAD_FOLDER'],file.filename))
                attachment = open("static/upload/"+file.filename,'rb')
                file_name = '=?utf-8?b?' + base64.b64encode(file.filename.encode()).decode() + '?='
                payload = MIMEBase('application', 'octet-stream')
                payload.add_header('Content-Disposition','attachment;filename= %s' % file_name)
                payload.set_payload((attachment).read())
                encoders.encode_base64(payload)
                msg.attach(payload)
                attachment.close()
        s = smtplib.SMTP('smtp.gmail.com',587)
        s.ehlo()
        s.starttls()
        s.login("joanne@dcard.cc","joannelin0818")
        text = msg.as_string().encode('utf-8')
        s.sendmail(sender,recipients,text)
        s.quit()
        return redirect('/')
    # if request.method == 'POST':
    #     msg_title = request.form['title']
    #     msg_recipients = [request.form['recipients']]
    #     msg_body = request.form['body']
    #     msg = Message(msg_title,msg_recipients,msg_body)
    #     mail.send(msg)
    #     return redirect('/')
    else:
        return render_template('send.html',contact=contact,emails=emails)

if __name__ == '__main__' :
    app.run(debug=True)
