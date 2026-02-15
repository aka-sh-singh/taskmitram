from celery.schedules import crontab
from typing import Dict, Any, Optional
from datetime import datetime

def check_workflow_schedule(
    frequency: str, 
    config: Dict[str, Any], 
    current_time: datetime
) -> bool:
    """
    Determines if a workflow should run at the current time based on its configuration.
    assumes current_time is in the same timezone as the schedule (UTC).
    """
    if not config:
        return False
        
    # 1. Time Check (HH:MM:SS)
    schedule_time_str = config.get("time") # "HH:MM" or "HH:MM:SS" in UTC
    if not schedule_time_str:
        return False
        
    try:
        parts = list(map(int, schedule_time_str.split(":")))
        hour = parts[0]
        minute = parts[1]
        second = parts[2] if len(parts) > 2 else 0
        
        scheduled_time_today = current_time.replace(hour=hour, minute=minute, second=second, microsecond=0)
        
        # If current time is before the scheduled time today, it's not time yet
        if current_time < scheduled_time_today:
            return False
            
    except Exception:
        return False
        
    # 2. Date/Day Checks
    freq = frequency.lower()
    
    if freq == "daily":
        return True
        
    elif freq == "weekly":
        # config["days"] should be list of ["mon", "tue", ...]
        allowed_days = [d.lower() for d in config.get("days", [])]
        current_weekday = current_time.strftime("%a").lower()
        return current_weekday in allowed_days
        
    elif freq == "monthly":
        return config.get("day_of_month") == current_time.day
        
    elif freq == "yearly":
        return (
            config.get("day_of_month") == current_time.day and 
            config.get("month") == current_time.month
        )
        
    elif freq == "once":
        # config["date"] should be "YYYY-MM-DD"
        target_date = config.get("date")
        if not target_date:
            return False
        current_date_str = current_time.strftime("%Y-%m-%d")
        return target_date == current_date_str
        
    # Custom/Cron not fully supported without croniter, but basic structure is here
    return False

def get_celery_schedule(frequency: str, config: Dict[str, Any]):
    """
    Converts user-friendly frequency and config into Celery Crontab or Schedule.
    """
    time = config.get("time", "00:00")
    try:
        hour, minute = map(int, time.split(":"))
    except ValueError:
        hour, minute = 0, 0
    
    if frequency == "daily":
        return crontab(hour=hour, minute=minute)
    
    elif frequency == "alternate":
        # Every 2 days
        return crontab(hour=hour, minute=minute, day_of_month="*/2")
    
    elif frequency == "weekly":
        # days: ["mon", "wed"]
        days = config.get("days", ["mon"])
        day_mapping = {
            "mon": 1, "tue": 2, "wed": 3, "thu": 4, "fri": 5, "sat": 6, "sun": 0
        }
        # Handle case where days might be None or empty
        if not days:
            return crontab(hour=hour, minute=minute)
            
        day_of_week = ",".join([str(day_mapping.get(d.lower(), 1)) for d in days])
        return crontab(hour=hour, minute=minute, day_of_week=day_of_week)
    
    elif frequency == "monthly":
        day_of_month = config.get("day_of_month", 1)
        return crontab(hour=hour, minute=minute, day_of_month=str(day_of_month))
    
    elif frequency == "yearly":
        day_of_month = config.get("day_of_month", 1)
        month_of_year = config.get("month", 1)
        return crontab(hour=hour, minute=minute, day_of_month=str(day_of_month), month_of_year=str(month_of_year))

    elif frequency == "custom_time":
        # config: { "cron": "0 0 * * *" }
        cron_str = config.get("cron", "0 0 * * *")
        cron = cron_str.split()
        if len(cron) == 5:
            return crontab(
                minute=cron[0],
                hour=cron[1],
                day_of_month=cron[2],
                month_of_year=cron[3],
                day_of_week=cron[4]
            )
            
    return crontab(hour=hour, minute=minute)

