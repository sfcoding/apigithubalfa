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

pythonPath = {'python-2.7':'/usr/bin/python', 'python-3.4': '/usr/bin/python3'}

@app.route('/')
def test():
    print 'branch ' + ' gitDir '
    logging.warning('Watch out!')
    return 'It runs'

@app.route('/post-update', methods=['GET','POST'])
def postUpdate():
    if request.method == 'POST':
        #path = request.args.get('path', '')
        data = request.json
        app.logger.debug(str(data))
        if not updateFolder(data):
            return "Not correct key "
        return 'All Right'
    else:
        return 'Request must be POST not GET [/post-update]'

@app.route('/post-updateFlask', methods=['GET','POST'])
def postUpdateFlask():
    if request.method == 'POST':
        #path = request.args.get('path', '')
        data = request.json
        wwwDir = '/var/www/'+data['repository']['name']

        if updateFolder(data) and os.path.exists(wwwDir+'/requirements.txt') and os.path.exists(wwwDir+'/runtime.txt'):
            venv = wwwDir + '/venv'
            if not os.path.isdir(venv):
                print 'create virtualenv'
                pathPy = getPythonPath(wwwDir+'/runtime.txt')
                if pathPy != None:
                    ris = subprocess.call(['/usr/local/bin/virtualenv', '-p '+pathPy, venv], stdout=subprocess.PIPE)
                else:
                    err = 'wrong python version'
                    app.logger.debug(err)
                    return err
            ris = subprocess.call([venv+'/bin/pip', 'install', '-r', wwwDir+'/requirements.txt'], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            ris = subprocess.call(['/usr/bin/touch', wwwDir+'/tmp/restart.txt'], stdout=subprocess.PIPE)
            app.logger.debug('ok '+str(ris))
            return 'ok'
        else:
            err = 'no requirements.txt or runtime.txt found'
            app.logger.debug(err)
            return err
    else:
        return 'Request must be POST not GET [/post-updateFlask]'

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
        return 'Request must be POST not GET [/post-updateNode]'

############################################################

def validate_signature():
    SECRET_KEY = os.environ['WSGI_ENV']
    sha_name,signature = request.headers.get("X-Hub-Signature").split("=")
    if sha_name != 'sha1':
        return False

    mac = hmac.new(SECRET_KEY,request.data, sha1)
    return mac.hexdigest()== signature                     # not secure evaluation find a solution

############################################################

def updateFolder(data):
    if not validate_signature():
        app.logger.debug("\n Error not validate signature check your key \n" )
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
        app.logger.debug('git folder found..' + str(ris))
    else:
        sshUrl = data['repository']['ssh_url']
        #ris = subprocess.call(['cd', wwwDir, '&&', 'git', 'clone', sshUrl])
        ris = subprocess.call(['git', 'clone', sshUrl, repoDir])
        app.logger.debug('git folder not found..' + str(ris))
    return True


def getPythonPath(runtimeFile):
    in_file = open(runtimeFile,"r")
    text = in_file.readline().strip()
    in_file.close()

    return pythonPath.get(text)
