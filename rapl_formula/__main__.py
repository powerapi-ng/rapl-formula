"""
Copyright (c) 2018, INRIA
Copyright (c) 2018, University of Lille
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import argparse
import logging
import signal
import zmq

from powerapi.cli.tools import CommonCLIParser
from powerapi.actor import ActorInitError
from powerapi.backendsupervisor import BackendSupervisor

from powerapi.dispatch_rule import HWPCDispatchRule, HWPCDepthLevel
from powerapi.filter import Filter
from powerapi.report import HWPCReport
from powerapi.dispatcher import DispatcherActor, RouteTable
from powerapi.cli.tools import generate_pullers, generate_pushers

from rapl_formula.rapl_formula_actor import RAPLFormulaActor


class BadActorInitializationError(Exception):
    """ Error if actor doesn't answer with "OKMessage" """


def launch_powerapi(config, logger):

    # Pusher
    pushers = generate_pushers(config)

    # Formula
    formula_factory = (lambda name, verbose:
                       RAPLFormulaActor(name, pushers, level_logger=verbose))

    # Dispatcher
    route_table = RouteTable()
    route_table.dispatch_rule(HWPCReport, HWPCDispatchRule(
        getattr(HWPCDepthLevel, 'ROOT'), primary=True))

    dispatcher = DispatcherActor('dispatcher', formula_factory, route_table,
                                 level_logger=config['verbose'])

    # Puller
    report_filter = Filter()
    report_filter.filter(lambda msg: True, dispatcher)
    pullers = generate_pullers(config, report_filter)

    # Setup signal handler
    def term_handler(_, __):
        for _, puller in pullers.items():
            puller.send_kill()

        dispatcher.send_kill()

        for _, pusher in pushers.items():
            pusher.send_kill()
        exit(0)

    signal.signal(signal.SIGTERM, term_handler)
    signal.signal(signal.SIGINT, term_handler)

    supervisor = BackendSupervisor(config['stream'])
    try:
        for _, pusher in pushers.items():
            supervisor.launch_actor(pusher)

        supervisor.launch_actor(dispatcher)

        for _, puller in pullers.items():
            supervisor.launch_actor(puller)

    except zmq.error.ZMQError as exn:
        logger.error('Communication error, ZMQError code : ' + str(exn.errno) +
                     ' reason : ' + exn.strerror)
        supervisor.kill_actors()
    except ActorInitError as exn:
        logger.error('Actor initialisation error, reason : ' + exn.message)
        supervisor.kill_actors()

    # wait
    supervisor.join()


def main(args=None):
    """
    Main function of the PowerAPI CLI
    """
    parser = CommonCLIParser()
    config = parser.parse_argv()

    logger = logging.getLogger('main_logger')
    logger.setLevel(config['verbose'])
    logger.addHandler(logging.StreamHandler())
    launch_powerapi(config, logger)


if __name__ == "__main__":
    main()
