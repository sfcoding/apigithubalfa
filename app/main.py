from flask import Flask, request, Response, jsonify
import logging
from logging.handlers import RotatingFileHandler
import subprocess
import os

########################

from hashlib import sha1
import hmac

########################

# LOG FILE
handler = RotatingFileHandler('apigithub.log', maxBytes=10000, backupCount=1)
formatter = logging.Formatter("[%(asctime)s] {%(module)s:%(lineno)d} %(levelname)s - %(message)s")
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)

app = Flask(__name__)

app.logger.addHandler(handler)
#app.setLevel(logging.DEBUG)
app.debug = True

@app.route('/')
def test():
    print 'branch ' + ' gitDir '
    logging.warning('Watch out!')
    return 'ciao'

@app.route('/post-update', methods=['GET','POST'])
def postUpdate():
    if request.method == 'POST':
        #path = request.args.get('path', '')
        data = request.json
        app.logger.debug(str(data))
        if not updateFolder(data):
            return "non e corretta la chiave"
        return ''
    else:
        return 'ciao'

@app.route('/post-updateFlask', methods=['GET','POST'])
def postUpdateFlask():
    if request.method == 'POST':
        #path = request.args.get('path', '')
        data = request.json
        wwwDir = '/var/www/'+data['repository']['name']

        if updateFolder(data) and os.path.exists(wwwDir+'/requirements.txt'):
            venv = wwwDir + '/venv'
            if not os.path.isdir(venv):
                print 'create virtualenv'
                ris = subprocess.call(['/usr/local/bin/virtualenv', venv], stdout=subprocess.PIPE)
            ris = subprocess.call([venv+'/bin/pip', 'install', '-r', wwwDir+'/requirements.txt'], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            ris = subprocess.call(['/usr/bin/touch', wwwDir+'/tmp/restart.txt'], stdout=subprocess.PIPE)
            app.logger.debug('fatto '+str(ris))
        else:
            app.logger.debug('no requirement.txt found')
        return ''
    else:
        return 'ciao'

@app.route('/post-updateNode', methods=['GET','POST'])
def postUpdateNode():
    if request.method == 'POST':
        #path = request.args.get('path', '')
        data = request.json
        wwwDir = '/var/www/'+data['repository']['name']

        if updateFolder(data) and os.path.exists(wwwDir+'/package.json'):

            ris = subprocess.call(['/usr/bin/npm', 'install', '--prefix', wwwDir], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            app.logger.debug('npm istallation '+str(ris))
            ris = subprocess.call(['/usr/bin/touch', wwwDir+'/tmp/restart.txt'], stdout=subprocess.PIPE)
            app.logger.debug('fatto '+str(ris))
        else:
            app.logger.debug('no package.json found')
        return ''
    else:
        return 'ciao'

############################################################

def validate_signature():
    SECRET_KEY = os.environ['WSGI_ENV']
    sha_name,signature = request.headers.get("X-Hub-Signature").split("=")
    if sha_name != 'sha1':
        return False

    mac = hmac.new(SECRET_KEY,request.data, sha1)
    return mac.hexdigest()== signature

############################################################

def updateFolder(data):
    if not validate_signature():
        app.logger.debug("\n \n\n\n Sono Falsoooooooo \n" )
        return False

    wwwDir = '/var/www/'
    #gitDir = '/home/git/repositories/'
    print 'NEW POST UPDATE EVENT START!'
    #wwwDir = wwwDir + path
    app.logger.debug(str(data['repository']['name']))

    repoDir = wwwDir + data['repository']['name']
    print repoDir
    if os.path.isdir(repoDir):
        #tmp = tmp.split(':')[1]
        #gitDir = gitDir + tmp
        #print gitDir
        #branch = data['ref']
        #ris = subprocess.call(['sudo', '-u', 'git', '-H', 'git', '--work-tree='+wwwDir, '--git-dir='+gitDir, 'checkout', '-f'])
        #ris = subprocess.call(['cd', repoDir, '&&', 'git', 'pull'])
        ris = subprocess.call(['git', '--work-tree='+repoDir, '--git-dir='+repoDir+'/.git', 'pull'])
        app.logger.debug(str(ris))
    else:
        sshUrl = data['repository']['ssh_url']
        #ris = subprocess.call(['cd', wwwDir, '&&', 'git', 'clone', sshUrl])
        ris = subprocess.call(['git', 'clone', sshUrl, repoDir])
        app.logger.debug(str(ris))
    return True
