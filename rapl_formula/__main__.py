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
from powerapi.actor import ActorInitError
from powerapi.backendsupervisor import BackendSupervisor
from powerapi.database import MongoDB
from powerapi.pusher import PusherActor
from powerapi.dispatch_rule import HWPCDispatchRule, HWPCDepthLevel
from powerapi.filter import Filter
from powerapi.puller import PullerActor
from powerapi.report import HWPCReport, PowerReport
from powerapi.report_model import HWPCModel
from powerapi.dispatcher import DispatcherActor, RouteTable
from rapl_formula.rapl_formula_actor import RAPLFormulaActor

class BadActorInitializationError(Exception):
    """ Error if actor doesn't answer with "OKMessage" """


def arg_parser_init():
    """ initialize argument parser"""
    parser = argparse.ArgumentParser(
        description="Start PowerAPI with the specified configuration.")

    # MongoDB input
    parser.add_argument("input_uri", help="MongoDB input uri")
    parser.add_argument("input_db", help="MongoDB input database")
    parser.add_argument("input_collection", help="MongoDB input collection")

    # MongoDB output
    parser.add_argument("output_uri", help="MongoDB output uri")
    parser.add_argument("output_db", help="MongoDB output database")
    parser.add_argument("output_collection", help="MongoDB output collection")

    # DispatchRule
    parser.add_argument("hwpc_dispatch_rule", help=
                        "Define the dispatch_rule rule, "
                        "Can be CORE, SOCKET or ROOT",
                        choices=['CORE', 'SOCKET', 'ROOT'])

    # Verbosity
    parser.add_argument("-v", "--verbose", help="Enable verbosity",
                        action="store_true", default=False)

    # Stream mode
    parser.add_argument("-s", "--stream_mode", help="Enable stream mode",
                        action="store_true", default=False)
    return parser


def launch_powerapi(args, logger):

    ##########################################################################
    # Actor Creation

    # Pusher
    output_mongodb = MongoDB(args.output_uri,
                             args.output_db, args.output_collection,
                             HWPCModel())
    pusher = PusherActor("pusher_mongodb", PowerReport, output_mongodb,
                         level_logger=args.verbose)

    # Formula
    formula_factory = (lambda name, verbose:
                       RAPLFormulaActor(name, pusher, level_logger=verbose))

    # Dispatcher
    route_table = RouteTable()
    route_table.dispatch_rule(HWPCReport, HWPCDispatchRule(
        getattr(HWPCDepthLevel, args.hwpc_dispatch_rule), primary=True))

    dispatcher = DispatcherActor('dispatcher', formula_factory, route_table,
                                 level_logger=args.verbose)

    # Puller
    input_mongodb = MongoDB(args.input_uri,
                            args.input_db, args.input_collection,
                            HWPCModel(), stream_mode=args.stream_mode)
    report_filter = Filter()
    report_filter.filter(lambda msg: True, dispatcher)
    puller = PullerActor("puller_mongodb", input_mongodb,
                         report_filter, level_logger=args.verbose)

    ##########################################################################
    # Actor start step

    # Setup signal handler
    def term_handler(_, __):
        puller.send_kill()
        dispatcher.send_kill()
        pusher.send_kill()
        exit(0)

    signal.signal(signal.SIGTERM, term_handler)
    signal.signal(signal.SIGINT, term_handler)

    supervisor = BackendSupervisor(puller.state.stream_mode)
    try:
        supervisor.launch_actor(pusher)
        supervisor.launch_actor(dispatcher)
        supervisor.launch_actor(puller)

    except zmq.error.ZMQError as exn:
        logger.error('Communication error, ZMQError code : ' + str(exn.errno) +
                     ' reason : ' + exn.strerror)
        supervisor.kill_actors()
    except ActorInitError as exn:
        logger.error('Actor initialisation error, reason : ' + exn.message)
        supervisor.kill_actors()

    ##########################################################################
    # Actor run step

    # wait
    supervisor.join()

    ##########################################################################


def main(args=None):
    """
    Main function of the PowerAPI CLI
    """
    args = arg_parser_init().parse_args()
    if args.verbose:
        args.verbose = logging.DEBUG

    logger = logging.getLogger('main_logger')
    logger.setLevel(args.verbose)
    logger.addHandler(logging.StreamHandler())
    launch_powerapi(args, logger)


if __name__ == "__main__":
    main()
