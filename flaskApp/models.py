from flaskApp.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


# 国家，省，市的数据都在这里
class StatisticData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # 不能为空，如果只有国家名称，没有省市的名称，则表示国家的数据
    countryName = db.Column(db.Text)
    # 如果有国家和省的名称，没有市的名称，则是省的数据
    provinceName = db.Column(db.Text)
    # 如果国家、省、市的名称都有，则是市的数据
    cityName = db.Column(db.Text)
    areaType = db.Column(db.Text)
    updateTime = db.Column(db.DateTime)
    confirmedCount = db.Column(db.Integer)
    suspectedCount = db.Column(db.Integer)
    curedCount = db.Column(db.Integer)
    deadCount = db.Column(db.Integer)
    def to_json(self):
        dict = self.__dict__
        # if "_sa_instance_state" in dict:
        #     del dict["_sa_instance_state"]
        return dict