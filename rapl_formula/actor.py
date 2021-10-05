# Copyright (c) 2021, INRIA
# Copyright (c) 2021, University of Lille
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE

from typing import Dict
from math import ldexp

from thespian.actors import ActorAddress

from powerapi.formula import AbstractCpuDramFormula, FormulaValues
from powerapi.message import FormulaStartMessage
from powerapi.report import HWPCReport, PowerReport

from .context import RAPLFormulaConfig


class RAPLValues(FormulaValues):
    """
    Initialize smartwatts values
    """
    def __init__(self, power_pushers: Dict[str, ActorAddress], config: RAPLFormulaConfig):
        """
        :param pushers: Pusher actors
        :param config: Configuration of the formula
        """
        FormulaValues.__init__(self, power_pushers)
        self.config = config


class RAPLFormulaActor(AbstractCpuDramFormula):
    """
    This actor handle the reports for the SmartWatts formula.
    """

    def __init__(self):
        AbstractCpuDramFormula.__init__(self, FormulaStartMessage)
        self.config = None

    def _initialization(self, message: FormulaStartMessage):
        AbstractCpuDramFormula._initialization(self, message)
        self.config = message.values.config

    def receiveMsg_HWPCReport(self, message: HWPCReport, _):
        """
        Process a HWPC report and send the result(s) to a pusher actor.
        :param msg: Received message
        :param state: Current actor state
        :return: New actor state
        :raise: UnknowMessageTypeException when the given message is not an HWPCReport
        """
        self.log_debug('received message ' + str(message))
        if 'rapl' not in message.groups:
            return

        reports = []
        for socket, socket_report in message.groups['rapl'].items():
            for events_counter in socket_report.values():
                for event, counter in events_counter.items():
                    if event.startswith('RAPL_'):
                        reports.append(self._gen_power_report(message.timestamp, socket,
                                                              counter))

        for _, actor_pusher in self.pushers.items():
            for result in reports:
                self.send(actor_pusher, result)

    def _gen_power_report(self, timestamp, target, counter):
        """
        Generate a power report using the given parameters.
        :param timestamp: Timestamp of the measurements
        :param target: Target name
        :param formula: Formula identifier
        :param power: Power estimation
        :return: Power report filled with the given parameters
        """

        metadata = {
            'scope': self.config.scope.value,
            'socket': self.socket,
        }

        power = ldexp(counter, -32)

        report = PowerReport(timestamp, self.sensor, target, power, metadata)

        return report
