from flaskApp.extensions import db
from flaskApp.models import StatisticData, LatestTime
from flaskApp.crawlerFromTencent import readnCoVFromTencent
from flaskApp.crawlerFromIsasclin import readOverallDataFromIsaaclin, readProvinceDataFromIsaaclin
from flaskApp.utils import logger
import click
import schedule
from datetime import datetime
import time


def do_crawl():
    data = readnCoVFromTencent()
    if len(data['data']) == 0:
        logger.warning('没有采集到数据')
        return False
    try:
        logger.info('开始写入数据...')
        
        for item in data['data']:
            db.session.add(item)
            db.session.commit()
        updateUpdateTime(data['updateTime'])

        logger.info('写入数据完成...')

        return True
    except BaseException as e:
        logger.error('抓取发生异常' + str(e))
        return False

def updateUpdateTime(newTime):
    try:
        oldData = LatestTime.query.first()
        if oldData:
            db.session.delete(oldData)
            db.session.commit()
        newData = LatestTime(updateTime=newTime)
        db.session.add(newData)
        db.session.commit()
        return True
    except BaseException as e:
        logger.warning('更新时间失败, ' +str(e))
        return False

def register_commands(app):
    
    @app.cli.command()
    def crawlprovincehistory():
        dataList = readProvinceDataFromIsaaclin()
        if len(dataList) == 0:
            logger.warning('没有采集到数据')
            return False
        try:
            logger.info('开始写入数据...')
            
            for item in dataList:
                db.session.add(item)
                db.session.commit()
            logger.info('写入数据完成...')
            return True
        except BaseException as e:
            logger.error('抓取发生异常, ' +str(e))
            return False

    @app.cli.command()
    def crawloverallhistory():
        dataList = readOverallDataFromIsaaclin()
        if len(dataList) == 0:
            logger.warning('没有采集到数据')
            return False
        try:
            logger.info('开始写入数据...')
            
            for item in dataList:
                db.session.add(item)
                db.session.commit()
            logger.info('写入数据完成...')
            return True
        except BaseException as e:
            logger.error('抓取发生异常,' + str(e))
            return False


    @app.cli.command()
    def crawl():
        try:
            do_crawl()
            schedule.every(15).minutes.do(do_crawl)
            while True:
                schedule.run_pending()
                time.sleep(1)
        except BaseException as e:
            logger.error('主循环异常退出, '+ str(e))

    @app.cli.command()
    def updatetime():
        updateUpdateTime(datetime(2020,1,29))