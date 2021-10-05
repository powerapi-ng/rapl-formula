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
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import pytest
import math

from thespian.actors import ActorExitRequest

from powerapi.formula import CpuDramDomainValues
from powerapi.message import StartMessage, FormulaStartMessage, ErrorMessage, EndMessage, OKMessage
from powerapi.report import Report, PowerReport, HWPCReport
from powerapi.test_utils.abstract_test import AbstractTestActor, recv_from_pipe
from powerapi.test_utils.actor import system
from powerapi.test_utils.dummy_actor import logger
import datetime

from rapl_formula.actor import RAPLValues, RAPLFormulaActor
from rapl_formula.context import RAPLFormulaScope, RAPLFormulaConfig

class TestRAPLFormula(AbstractTestActor):
    @pytest.fixture
    def actor(self, system):
        actor = system.createActor(RAPLFormulaActor)
        yield actor
        system.tell(actor, ActorExitRequest())

    @pytest.fixture
    def actor_start_message(self, logger):
        config = RAPLFormulaConfig(RAPLFormulaScope.CPU, 1000, 'RAPL_ENERGY_PKG')
        values = RAPLValues({'logger': logger},config)
        return FormulaStartMessage('system', 'test_rapl_formula', values, CpuDramDomainValues('test_device', ('test_sensor', 0, 0)))

    def test_starting_rapl_formula_without_raplFormulaStartMessage_answer_ErrorMessage(self, system, actor):
        answer = system.ask(actor, StartMessage('system', 'test'))
        assert isinstance(answer, ErrorMessage)
        assert answer.error_message == 'use FormulaStartMessage instead of StartMessage'

    def test_send_hwpc_report_to_rapl_formula_return_correct_result(self, system, started_actor, dummy_pipe_out):
        report = HWPCReport.from_json(
            {"timestamp": "2021-10-05T09:14:58.226",
              "sensor": "toto",
              "target": "all",
              "groups":
              {"rapl":
               {"0":
                {"7":
                 {"RAPL_ENERGY_PKG": 5558763520.0,
                  "time_enabled": 1000770053.0,
                  "time_running": 1000770053.0
                  }
                 }
                }
               }
             }
        )

        system.tell(started_actor,report)

        _, msg = recv_from_pipe(dummy_pipe_out, 1)

        assert isinstance(msg,PowerReport)
        assert msg.power ==  math.ldexp(5558763520.0, -32)
