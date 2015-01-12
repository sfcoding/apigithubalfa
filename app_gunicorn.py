import sys
sys.path.append('/var/www/apigithubalfa')
from app.main import app as application

application.run(debug=True)
