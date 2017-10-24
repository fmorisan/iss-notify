# -*- coding: utf-8 -*-
import json
import logging
import time
from pytz import utc
from datetime import datetime, timedelta
from huey import crontab
import folium

import settings
from main import huey, redis
from services import OneSignal
from tle import SatTracker
from schema import ISSPass, db

logger = logging.getLogger(__name__)


@huey.task(include_task=True)
def alert(location, data, task=None):
    redis.srem('iss:schedule:%s' % location, task.task_id)

    if datetime.utcnow() < data['end']['datetime']:
        logger.info("ISS above on %s!" % location)
        OneSignal().send_pass_notification(location, data)


interval = crontab(minute=settings.CHECK_INTERVAL_MINUTES)
@huey.periodic_task(interval)
def schedule():
    """Schedule passes for all locations that hasn't pending passes"""

    for location in redis.smembers('iss:locations'):

        schedule = 'iss:schedule:%s' % location

        if redis.exists(schedule):
            continue

        lat, lng = location.split(',')
        ha = SatTracker(lat, lng)

        for next_pass in ha.get_next_passes():
            logger.info("Scheduling ISS pass for %s" % location)

            pass_start = next_pass['start']['datetime'].replace(tzinfo=utc)

            # Save pass in SQLite
            iss_pass = ISSPass(
                lat=lat,
                lng=lng,
                start_date=pass_start,
                path=next_pass.get('path', [])
            )
            db.add(iss_pass)
            db.commit()

            # Schedule pass in Redis
            q = alert.schedule(
                args=[location, next_pass, iss_pass.id],
                eta=start_pass
            )

            redis.sadd(schedule, q.task.task_id)

        # Limit requests
        time.sleep(2)


interval = crontab(hour=0)
@huey.periodic_task(interval)
def map():
    fmap = folium.Map(tiles='CartoDB dark_matter')
    bounds = []

    for loc in redis.smembers('iss:locations'):
        coords = [float(v) for v in loc.split(',')]
        bounds.append(coords)
        folium.Marker(location=coords).add_to(fmap)

    fmap.fit_bounds(bounds)
    fmap.save(settings.MAP_FILE)
