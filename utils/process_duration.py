from datetime import datetime, timedelta, date, time, timezone
from dateutil.rrule import *
from django.utils import timezone
import pytz
# from django.conf import settings




def get_localized_time(date: date, time: time,) -> datetime:
    """Returns a localized date time"""
    timezone = pytz.timezone('Africa/Lagos')
    return timezone.localize(datetime.combine(date, time))


def converStringToDate(strDate:str)->date:
    return datetime.strptime(strDate,'%Y-%m-%d').date()


def converStringToTime(strTime:str)->time:
    return datetime.strptime(strTime,'%H:%M:%S').time()

def convertStringToTimeAndAddSomeHours(strTime:str,hour:int)->time:
    datetimeObj = datetime.strptime(strTime,'%H:%M:%S')
    datetimeObj = datetimeObj + timedelta(hours=hour)
    return datetimeObj.time()
