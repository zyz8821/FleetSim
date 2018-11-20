#!/usr/bin/env python

from datetime import datetime
import logging
import simpy
import os

from vppsim.entities import EV, VPP
from vppsim import loader

# PHYSICAL CONSTANTS
MAX_EV_CAPACITY = 16.5  # kWh
MAX_EV_RANGE = 20       # km
CHARGING_SPEED = 3.6    # 3.6 kWh per hour


def main():
    os.makedirs('./logs', exist_ok=True)

    logging.basicConfig(level=logging.DEBUG,
                    format='%(name)-10s: %(levelname)-7s %(message)s',
                    filename='./logs/sim-%s.log' % datetime.now().strftime('%Y%m%d-%H%M%S'),
                    filemode='w')
    logger = logging.getLogger('vppsim')


    df = loader.load()
    num_evs = len(df.EV.unique())

    env = simpy.Environment(initial_time=df.start_time.min())
    vpp = VPP(env, 1, num_evs)
    env.process(lifecycle(logger, env, vpp, df))

    logger.info('[%s] - ---- STARTING SIMULATION -----' % datetime.fromtimestamp(env.now))
    env.run(until=df.end_time.max())


def lifecycle(logger, env, vpp, df):
    evs = {}
    previous = df.iloc[0,:]

    for rental in df.itertuples():

        # Wait until next rental
        yield env.timeout(rental.start_time - previous.start_time)  # sec

        if rental.EV not in evs:
            logger.info('[%s] - ---------- NEW EV %d ----------' % (datetime.fromtimestamp(env.now), rental.Index))
            evs[rental.EV] = EV(env, vpp, rental.EV, rental.start_soc)

        ev = evs[rental.EV]
        env.process(ev.drive(env, rental.Index, rental.trip_duration,
                             rental.start_soc - rental.end_soc,
                             rental.start_soc, rental.end_charging))
        previous = rental


if __name__ == '__main__':
    main()
