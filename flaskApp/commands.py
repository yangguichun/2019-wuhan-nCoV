from flaskApp.extensions import db
from flaskApp.models import DataLogs, LatestTime, Area, DayCaches
from flaskApp.crawler.crawlerFromTencent import readnCoVFromTencent
from flaskApp.crawler.crawlerAreaTencent import readnAreaFromTencent
from flaskApp.crawler.crawlerFromIsasclin import readOverallDataFromIsaaclin, readProvinceDataFromIsaaclin
from flaskApp.crawler.crawlerFromIsasclinReal import readnCovFromIsasclin
from flaskApp.crawler.crawlPosition import readPositionFromBaidu
from flaskApp.utils import logger
from sqlalchemy import and_, distinct, text

import click
import schedule
from datetime import datetime, timedelta
import time
    
def updateOneDayCachesLog(data):
    updateTime = data.updateTime.strftime('%Y-%m-%d')
    cacheLog = DayCaches.query.filter(and_(DayCaches.countryName==data.countryName, DayCaches.provinceName==data.provinceName, DayCaches.cityName==data.cityName, DayCaches.updateTime==updateTime)).first()
    if cacheLog:
        # logger.info('updateOneDayCachesLog update, %s', cacheLog.to_json())
        cacheLog.confirmedCount = data.confirmedCount
        cacheLog.suspectedCount = data.suspectedCount
        cacheLog.curedCount = data.curedCount
        cacheLog.deadCount = data.deadCount
        db.session.commit()
    else:
        # logger.info('updateOneDayCachesLog insert, %s', cacheLog)
        cacheLog = DayCaches()
        cacheLog.updateTime = updateTime
        cacheLog.countryName = data.countryName
        cacheLog.provinceName = data.provinceName
        cacheLog.cityName = data.cityName
        cacheLog.confirmedCount = data.confirmedCount
        cacheLog.suspectedCount = data.suspectedCount
        cacheLog.curedCount = data.curedCount
        cacheLog.deadCount = data.deadCount
        db.session.add(cacheLog)
        db.session.commit()

def updateToDayCaches(datalogList):
    logger.info('开始更新到缓存表...')
    try:
        for data in datalogList:
            updateOneDayCachesLog(data)
    except BaseException as e:
        logger.error('写入缓存表发生异常' + str(e))
        return False
    logger.info('完成缓存表更新')
    return True

def do_crawl():
    # data = readnCoVFromTencent()
    data = readnCovFromIsasclin()
    if len(data['data']) == 0:
        logger.warning('没有采集到数据')
        return False
    try:
        logger.info('开始写入数据...')
        
        if not updateToDayCaches(data['data']):
            return False

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
    def crawlarea():
        dataList = readnAreaFromTencent()
        if len(dataList) == 0:
            logger.warning('没有采集到数据')
            return False
        try:
            logger.info('开始写入数据...')
            counter = 0
            for item in dataList:
                # counter += 1
                if item.level != 'country':
                    pos = readPositionFromBaidu(item.name, item.parentName)
                    if pos:
                        item.longitude = pos["lng"]
                        item.latitude = pos["lat"]
                db.session.add(item)
                db.session.commit()
                # if counter > 10:
                #     break
                
            logger.info('写入数据完成...')
            return True
        except BaseException as e:
            logger.error('抓取发生异常,' + str(e))
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

    def queryOneDay(theday):
        startDate = theday.strftime('%Y-%m-%d')
        endDate = (theday + timedelta(1)).strftime('%Y-%m-%d')
        logger.info('queryOneDay, %s, %s', startDate, endDate)
        dataList = DataLogs.query.distinct(DataLogs.countryName,DataLogs.provinceName, DataLogs.cityName).filter(and_(DataLogs.updateTime>startDate, DataLogs.updateTime<endDate)).order_by(DataLogs.countryName,DataLogs.provinceName, DataLogs.cityName, DataLogs.updateTime.desc()).all()
        logger.info('queryOneDay, count %d', len(dataList))
        for data in dataList:
            dayData = DayCaches(countryName=data.countryName, provinceName=data.provinceName, cityName=data.cityName, confirmedCount=data.confirmedCount, suspectedCount=data.suspectedCount, curedCount=data.curedCount, deadCount=data.deadCount)
            dayData.updateTime = theday
            db.session.add(dayData)
            db.session.commit()
        
        
    @app.cli.command()
    def cachedata():
        startDate = datetime(2020,2,3,0,0,0,0)
        endDate = datetime(2020,2,4,0,0,0,0)
        oneDay = timedelta(1)
        while startDate<endDate:
            logger.info('转存%s数据', startDate)
            queryOneDay(startDate)
            startDate = startDate + oneDay


    @app.cli.command()
    def updatetime():
        updateUpdateTime(datetime(2020,1,29))
    
    @app.cli.command()
    def testupdate():
        dayLog = DayCaches.query.filter(and_(DayCaches.countryName =='全球', DayCaches.updateTime=='2020-02-02')).first()
        # dayLog = DayCaches.query.first()
        logger.info(dayLog.to_json())
        dayLog.confirmedCount = 14411
        db.session.commit()

    @app.cli.command()
    def testsql():
        # dataList = DataLogs.query.distinct(DataLogs.countryName,DataLogs.provinceName, DataLogs.cityName).filter(and_(DataLogs.updateTime>'2020-01-30', DataLogs.updateTime<'2020-01-31')).order_by(DataLogs.countryName,DataLogs.provinceName, DataLogs.cityName, DataLogs.updateTime.desc()).all()
        # nameList = ','.join(['\'武汉\'', '\'深圳\''])
        # sql = f'name in ( {nameList} )' 
        nameList = ['\'武汉\'', '\'深圳\'']
        nameStr = ','.join(nameList)
        sql = f'name in ({nameStr})' 
        dataList = Area.query.filter(text(sql)).all()
        logger.info('count is %d', len(dataList))
        for item in dataList:
            logger.info(item.to_json())
            # logger.info("%s %s", item.cityName, item.updateTime)