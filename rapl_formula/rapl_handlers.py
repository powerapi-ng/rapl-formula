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

import math

from powerapi.handler import Handler
from powerapi.report import PowerReport


class RAPLHandler(Handler):
    """
    RAPLHandler class
    """
    def __init__(self, state):
        """
        RAPLHandler initialization
        """
        super().__init__(state)

    def _estimate(self, report):
        """
        Method that estimate the power consumption from an input report
        :param report: Input Report
        :return: List of PowerReport
        """
        def gen_power_report(report, socket, event, counter):
            """
            Generate a power report for a RAPL event.

            :param report: HWPC report
            :param socket: Socket ID
            :param event: RAPL event name
            :param counter: RAPL event counter
            """
            power = math.ldexp(counter, -32)
            metadata = {'socket': socket, 'event': event}
            return PowerReport(report.timestamp, report.sensor, report.target,
                               power, metadata)

        if 'rapl' not in report.groups:
            return []

        reports = []
        for socket, socket_report in report.groups['rapl'].items():
            if len(self.state.formula_id) < 3 or int(self.state.formula_id[2]) == int(socket):
                for events_counter in socket_report.values():
                    for event, counter in events_counter.items():
                        if event.startswith('RAPL_'):
                            reports.append(gen_power_report(report, socket,
                                                            event, counter))
        return reports

    def handle(self, msg):
        """
        Process a report and send the result to the pusher actor
        :param powerapi.Report msg:  Received message
        :return: New Actor state
        :rtype:  powerapi.State
        :raises UnknowMessageTypeException: If the msg is not a Report
        """
        results = self._estimate(msg)
        for _, actor_pusher in self.state.pushers.items():
            for result in results:
                actor_pusher.send_data(result)
