from datetime import datetime
import uuid
from services.db import db

class XUUpload(db.Model):
    __tablename__ = "XU_UPLOAD"
    __table_args__ = {"schema": "DP_APPL_XLS_UPLOAD"}
    id = db.Column("ID", db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticketno = db.Column("TICKETNO", db.Integer, nullable=False, unique=True)
    applicationcode = db.Column("APPLICATIONCODE", db.String(20), nullable=False)
    filtercode = db.Column("FILTERCODE", db.String(20), nullable=False)
    outputcode = db.Column("OUTPUTCODE", db.String(20), nullable=True)
    username = db.Column("USERNAME", db.String(40), nullable=False, default="local-user")
    uploadstartdate = db.Column("UPLOADSTARTDATE", db.DateTime, nullable=False, default=datetime.utcnow)
    uploadenddate = db.Column("UPLOADENDDATE", db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column("DESCRIPTION", db.String(50), nullable=False)
    rowcount = db.Column("ROWCOUNT", db.Integer, nullable=False)
    filename = db.Column("FILENAME", db.String(250), nullable=False)
    stampedfilename = db.Column("STAMPEDFILENAME", db.String(250), nullable=True)
    userip = db.Column("USERIP", db.String(50), nullable=True)
    sha2hash = db.Column("SHA2HASH", db.String(250), nullable=True)
    uploadstatusid = db.Column("UPLOADSTATUSID", db.Integer, nullable=False, default=1)

class XUUploadDataV2(db.Model):
    __tablename__ = "XU_UPLOADDATA_V2"
    __table_args__ = {"schema": "DP_APPL_XLS_UPLOAD"}
    id = db.Column(db.Integer, primary_key=True)
    upload_id = db.Column("UPLOADID", db.String(36), nullable=False)
    upload_data = db.Column("UPLOADDATA", db.String(40), nullable=False)
    process_file_name = db.Column("PROCESS_FILE_NAME", db.String(300), nullable=False)
    extra_info1 = db.Column("EXTRA_INFO1", db.String(100))
    extra_info2 = db.Column("EXTRA_INFO2", db.String(100))
    extra_info3 = db.Column("EXTRA_INFO3", db.String(100))
    extra_info4 = db.Column("EXTRA_INFO4", db.String(100))
    extra_info5 = db.Column("EXTRA_INFO5", db.String(100))
    extra_info6 = db.Column("EXTRA_INFO6", db.String(100))
    extra_info7 = db.Column("EXTRA_INFO7", db.String(100))
    extra_info8 = db.Column("EXTRA_INFO8", db.String(100))
    extra_info9 = db.Column("EXTRA_INFO9", db.String(100))
    extra_info10 = db.Column("EXTRA_INFO10", db.String(100))
