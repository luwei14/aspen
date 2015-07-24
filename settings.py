"""
Settings for aspen.py
"""
import os

app_path = os.path.dirname(__file__)

#system
CACHE = False
DEBUG = True

# database
DBTYPE = 'sqlite'
DATAPATH = app_path+"/data/site.db"

TBL_USER = "tbl_user"
TBL_POST = "tbl_post"
TBL_CATEGORY = "tbl_category"
TBL_TAG = "tbl_tag"


