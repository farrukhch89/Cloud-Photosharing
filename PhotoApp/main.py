from audioop import getsample
import datetime
from flask import Flask, render_template, request, redirect, Response
from google.cloud import datastore
from google.cloud import storage
import google.oauth2.id_token
from google.auth.transport import requests
import local_constants as local_constants

app = Flask(__name__)

# get access to the datastore client so we can add and store data in the datastore
datastore_client = datastore.Client()

# get access to a request adapter for firebase as we will need this to authenticate users
firebase_request_adapter = requests.Request()

def createUserInfo(claims):
    entity_key = datastore_client.key('UserInfo', claims['email'])
    entity = datastore.Entity(key = entity_key)
    entity.update({
        'email': claims['email'],
    })
    datastore_client.put(entity)
    addDirectory(claims['email'] + '/')

def retrieveUserInfo(claims):
    entity_key = datastore_client.key('UserInfo', claims['email'])
    entity = datastore_client.get(entity_key)
    return entity

def blobList(prefix):
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    return storage_client.list_blobs(local_constants.PROJECT_STORAGE_BUCKET,
prefix=prefix)

def addDirectory(directory_name):
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    blob = bucket.blob(directory_name)
    blob.upload_from_string('', content_type='application/x-www-form-urlencoded;charset=UTF-8')

def addInFile(direct, file):
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    blob = bucket.blob(direct+ file.filename)
    blob.content_type = 'image/jpeg'
    blob.upload_from_file(file)

def addFile(file):
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    blob = bucket.blob(file.filename)
    blob.upload_from_file(file)

def downloadBlob(filename):
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    blob = bucket.blob(filename)
    return blob.download_as_bytes()

def showimage(filename):
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    blob = bucket.blob(filename)
    url_lifetime = 3600  # Seconds in an hour
    serving_url = blob.generate_signed_url(url_lifetime)
    return serving_url



def deleteBlob(direct):
    
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    blob = bucket.blob(direct)
    blob.delete()

def deleteDirectBlob(direct):
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    blob = bucket.blob(direct)
    blob.delete()

def getSize(direct):
    storage_size = 0
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    blob_list = blobList(direct)

    for i in blob_list:
        blob_name = i.name
        blob = bucket.get_blob(blob_name)
        storage_size = storage_size+blob.size

    storage_size = storage_size/1000000
    storage_size = round(storage_size, 2)

    return storage_size

@app.route('/show/<string:filename>', methods=['POST'])
def showFile(directory_name):
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None
    user_info = None
    file_bytes = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
firebase_request_adapter)
            direct = claims['email'] + '/' + directory_name
            showimage(direct)
        except ValueError as exc:
            error_message = str(exc)
    return redirect('/')

@app.route('/delete_dir/<string:filename>', methods=['POST'])
def deleteDir(directory_name):
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None
    user_info = None
    file_bytes = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
firebase_request_adapter)
            directory_name.replace('/','')
            direct = claims['email'] + '/' + directory_name
            
            deleteBlob(direct)
        except ValueError as exc:
            error_message = str(exc)
    return redirect('/')

@app.route('/delete_file/<string:filename>', methods=['POST'])
def deleteFile(filename):
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None
    user_info = None
    file_bytes = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
firebase_request_adapter)
            direct = claims['email'] + '/' + filename
            deleteBlob(direct)
        except ValueError as exc:
            error_message = str(exc)
    return redirect('/')

@app.route('/add_directory', methods=['POST'])
def addDirectoryHandler():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None
    user_info = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
firebase_request_adapter)
            directory_name = request.form['dir_name']
            if directory_name == '' or directory_name[len(directory_name) - 1] != '/':
                directory_name = directory_name +'/'
            user_info = retrieveUserInfo(claims)
            direct = claims['email'] + '/'+ directory_name
            addDirectory(direct)
        except ValueError as exc:
            error_message = str(exc)
    return redirect('/')

@app.route('/upload_file', methods=['post'])
def uploadFileHandler():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None
    user_info = None
    storage = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
firebase_request_adapter)
            file = request.files['file_name']
            user_info = retrieveUserInfo(claims)
            direct = claims['email'] + '/'
            storage = getSize(direct)
            if (storage < 50):
                addInFile(direct,file)
            else:
                error_message = "Storage Full"
        except ValueError as exc:
            error_message = str(exc)
    return redirect('/')

@app.route('/download_file/<string:filename>', methods=['POST'])
def downloadFile(filename):
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None
    user_info = None
    file_bytes = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)
    return Response(downloadBlob(filename), mimetype='application/octet-stream')

@app.route('/gallery')
def showGallery():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None
    user_info = None
    image_list = []
    file_list = []
    direct = None
    storage_size = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
firebase_request_adapter)
            user_info = retrieveUserInfo(claims)
            if user_info == None:
                createUserInfo(claims)
                user_info = retrieveUserInfo(claims)
            direct = claims['email'] + '/'
            blob_list = blobList(direct)
            storage_size = getSize(direct)
            for i in blob_list:
                if i.name[len(i.name) - 1] == '/':
                    file_list.append(i)
                else:
                    image_list.append(i)
        except ValueError as exc:
            error_message = str(exc)
    return render_template('gallery.html', user_data=claims, error_message=error_message,
user_info=user_info, file_list=file_list, image_list=image_list, direct = direct, storage_size =storage_size)

@app.route('/')
def root():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None
    user_info = None
    file_list = []
    directory_list = []
    direct = None
    storage_size = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
firebase_request_adapter)
            user_info = retrieveUserInfo(claims)
            if user_info == None:
                createUserInfo(claims)
                user_info = retrieveUserInfo(claims)
            direct = claims['email'] + '/'
            blob_list = blobList(direct)
            storage_size = getSize(direct)
            for i in blob_list:
                if i.name[len(i.name) - 1] == '/':
                    directory_list.append(i)
                else:
                    file_list.append(i)
        except ValueError as exc:
            error_message = str(exc)
    return render_template('index2.html', user_data=claims, error_message=error_message,
user_info=user_info, file_list=file_list, directory_list=directory_list, direct = direct, storage_size =storage_size)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
