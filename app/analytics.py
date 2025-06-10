from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime
from app import database, models, schemas
from sqlalchemy import Date

router = APIRouter()

@router.get("/analytics/{user_id}", response_model=schemas.AnalysisResult)
def analyze_user_activity(user_id: int, db: Session = Depends(database.get_db)):
    today = date.today()

    events_today = db.query(models.Event).filter(
        models.Event.user_id == user_id,
        models.Event.date.cast(Date) == today
    ).all()

    tasks_today = db.query(models.Task).filter(
        models.Task.user_id == user_id,
        models.Task.deadline.cast(Date) == today
    ).all()

    recs = []

    if len(events_today) >= 5:
        recs.append("You have many events scheduled for today. Consider taking a break or rescheduling some of them.")
    if len(tasks_today) >= 7:
        recs.append("You have too many tasks. Try prioritizing them.")


    all_tasks = db.query(models.Task).filter(
        models.Task.user_id == user_id
    ).all()

    high_priority_tasks = [task for task in all_tasks if task.priority.lower() == "high" and not task.is_done]
    if len(high_priority_tasks) >= 3:
        recs.append("You have many high-priority tasks. Consider delegating some or breaking them into smaller steps.")

    if len(all_tasks) >= 8:
        recs.append("You have too many tasks. Try prioritizing or postponing less important ones.")

    overdue_tasks = [task for task in all_tasks if task.deadline < datetime.now() and not task.is_done ]

    if overdue_tasks:
        recs.append("You have overdue tasks. Consider addressing them first.")

    low_priority_tasks = [task for task in all_tasks if task.priority.lower() == "low"]

    if len(all_tasks) > 0 and len(low_priority_tasks) / len(all_tasks) > 0.5:
        recs.append("Many of your tasks are low-priority. Make sure you are focusing on what really matters.")

    completed_today = [task for task in all_tasks if task.is_done and task.deadline.date() == today]

    if all_tasks and len([task for task in all_tasks if task.is_done]) < len(all_tasks) / 2:
        recs.append( "More than half of your tasks  are still pending. Try to focus on completing the most important ones.")

    if len(all_tasks) == 0 and len(events_today) == 0:
        recs.append("Your schedule is clear for today. Consider planning or learning something new!")

    from datetime import time

    late_time = time(20, 0)

    has_late_event = any(event.date.time() > late_time for event in events_today)
    has_late_task = any(task.deadline.time() > late_time for task in tasks_today)

    if has_late_event or has_late_task:
        recs.append("You have late activities today. Don't forget to rest and maintain work–life balance.")

    midday_start = time(11, 0)
    midday_end = time(15, 0)

    midday_events = [event for event in events_today if midday_start <= event.date.time() <= midday_end]
    midday_tasks = [task for task in tasks_today if midday_start <= task.deadline.time() <= midday_end]

    if len(midday_events) + len(midday_tasks) > 2:
        recs.append("Your midday looks busy. Make sure to take time for lunch or a short walk.")

    if all(task.priority.lower() == "low" for task in all_tasks) and all_tasks:
        recs.append("All your tasks have low priority. Consider reviewing your goals for the day.")

    if all_tasks and all(not task.is_done for task in all_tasks):
        recs.append("You haven't completed any tasks yet. Try starting with something small.")

    today_tasks = [task for task in all_tasks if task.deadline.date() == today]


    if all_tasks and all(task.is_done for task in all_tasks):
        recs.append("Excellent! You've completed all your tasks.")
    elif today_tasks and all(task.is_done for task in today_tasks):
        recs.append("Excellent! You've completed all your tasks for today.")


    if not recs:
        recs.append("Your schedule for today looks balanced.")


    return {"recommendation": recs}