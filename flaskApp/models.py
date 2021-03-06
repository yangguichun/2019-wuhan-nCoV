from flaskApp.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class Area(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    parentName = db.Column(db.Text)
    level = db.Column(db.Text)

    longitude = db.Column(db.Float) 
    latitude = db.Column(db.Float) 
    def to_json(self):
        dict = self.__dict__
        return dict
     
# 用来存储最新数据市标，这样就可以知道最新的数据是否有更新
class LatestTime(db.Model):
    updateTime = db.Column(db.DateTime, primary_key=True)
    def to_json(self):
        dict = self.__dict__
        return dict

# 国家，省，市的数据都在这里
class DataLogs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # 不能为空，如果只有国家名称，没有省市的名称，则表示国家的数据
    countryName = db.Column(db.Text)
    # 如果有国家和省的名称，没有市的名称，则是省的数据
    provinceName = db.Column(db.Text)
    # 如果国家、省、市的名称都有，则是市的数据
    cityName = db.Column(db.Text)
    updateTime = db.Column(db.DateTime, index=True)
    confirmedCount = db.Column(db.Integer)
    suspectedCount = db.Column(db.Integer)
    curedCount = db.Column(db.Integer)
    deadCount = db.Column(db.Integer)
    def to_json(self):
        dict = self.__dict__
        # if "_sa_instance_state" in dict:
        #     del dict["_sa_instance_state"]
        return dict

class ApiLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    logTime = db.Column(db.DateTime, index=True)
    api = db.Column(db.Text)
    params = db.Column(db.Text)
    remoteAddr = db.Column(db.Text)
    def to_json(self):
        dict = self.__dict__
        return dict

class DayCaches(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # 不能为空，如果只有国家名称，没有省市的名称，则表示国家的数据
    countryName = db.Column(db.Text)
    # 如果有国家和省的名称，没有市的名称，则是省的数据
    provinceName = db.Column(db.Text)
    # 如果国家、省、市的名称都有，则是市的数据
    cityName = db.Column(db.Text)
    updateTime = db.Column(db.DateTime, index=True)
    confirmedCount = db.Column(db.Integer)
    suspectedCount = db.Column(db.Integer)
    curedCount = db.Column(db.Integer)
    deadCount = db.Column(db.Integer)
    def to_json(self):
        dict = self.__dict__
        # if "_sa_instance_state" in dict:
        #     del dict["_sa_instance_state"]
        return dict