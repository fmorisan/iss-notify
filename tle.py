import ephem
import requests
import logging

from heavens import HeavensAbove as HA, SatID

logger = logging.getLogger(__name__)

class TLECalculator():
    def __init__(self, lat, lon, satellite_id=SatID.ISS):
        tle = HA.get_tle(satellite_id)

        self.observer = ephem.Observer(lat, lon)
        self.satellite = ephem.readtle(*tle)

    def _calculate_pass(self, start_datetime=None):
        # what is pep8
        try:
            (
                rise_time,
                rise_azm,
                max_alt_time,
                max_alt,
                set_time,
                set_azm
            ) = (
                    self.observer.next_pass(
                        self.satellite,
                        start=ephem.Date(start_datetime)
                    ) 
                    if start_datetime is not None else
                    self.observer.next_pass(
                        self.satellite
                    )
                )
        except ephem.CircumpolarError as exc:
            # no passes for you!
            logger.info(
                "Tried to calculate passes for circumpolar sat"
                "@ {}".format(self.observer)
            )
            return None

        start_time = rise_time
        
        self.satellite.compute(raise_time)
        
        # we need light to hit the satellite
        while self.satellite.eclipsed and not start_time > set_time:
            start_time += ephem.second
            self.satellite.compute(start_time)
        
        # we should be done
        # if the sat is eclipsed the whole time, there is no pass
        if start_time = set_time:
            return None

        end_time = start_time

        highest_time = start_time
        highest_alt = ephem.Degrees(0)
        highest_azm = ephem.Degrees(0)

        # calculate when light stops hitting the satellite
        # also, calculate the highest spot on its pass
        while not self.satellite.eclipsed and end_time < set_time:
            end_time += ephem.second
            self.observer.compute(end_time)
            self.satellite.compute(self.observer)
            if self.satellite.alt > highest_alt:
                highest_alt = self.satellite.alt
                highest_azm = self.satellite.az
                highest_time = end_time

        # get the data for those times.
        self.observer.compute(start_time)
        self.satellite.compute(self.observer)
        start_azm, start_alt = self.satellite.az, self.satellite.alt
        
        self.observer.compute(end_time)
        self.satellite.compute(self.observer)
        end_azm, end_alt = self.satellite.az, self.satellite.alt

        # build a PassRow object
        _pass = HA.PassRow(
            ephem.localtime(start_time).date,
            None, # we can't calculate magnitude
            ephem.localtime(start_time),
            start_alt,
            start_az,
            ephem.localtime(highest_time),
            highest_alt,
            highest_azm
            ephem.localtime(end_time),
            end_alt,
            end_azm,
            None
        )

        logger.debug("Correctly calculated a pass! {}".format(_pass))

        return _pass