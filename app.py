# -*- encoding: utf-8 -*-
"""
Flask Boilerplate
Author: AppSeed.us - App Generator 
"""

import os
from app import app
from app import db
from flask_cors import CORS
#----------------------------------------
# launch
#----------------------------------------
CORS(app)
if __name__ == "__main__":
	db.create_all()

	port = int(os.environ.get("PORT", 5000))
	app.run(host='0.0.0.0', port=port, debug=True)
	#app.run(ssl_context='adhoc')

    