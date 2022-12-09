from termcolor import colored
from typing import List

from sc_client import client

from sc_client.models import ScAddr, ScTemplate, ScLinkContent
from sc_client.constants import sc_types

from sc_kpm import ScAgentClassic, ScResult, ScKeynodes

from sc_kpm.utils.action_utils import get_action_arguments
from sc_kpm.utils import create_edge
from sc_kpm.utils.creation_utils import create_node, create_structure, wrap_in_set
from sc_kpm.utils.common_utils import get_system_idtf
from sc_kpm.logging import get_kpm_logger


_logger = get_kpm_logger()

class SearchCollegeByRegionAgent(ScAgentClassic):
    def __init__(self):
        super().__init__("action_search_college_by_region")
        self._keynodes = ScKeynodes()

    def on_event(self, class_node: ScAddr, edge: ScAddr, action_node: ScAddr) -> ScResult:
        if not self._confirm_action_class(action_node):
            return ScResult.SKIP

        status = ScResult.OK
        _logger.debug("SearchCollegeByRegionAgent starts")

        try:
            _logger.debug("SearchCollegeByRegionAgent get arguments")

            if action_node is None or not action_node.is_valid():
                _logger.debug("Not Valid node")
                raise Exception("The question node isn't valid")

            node, = get_action_arguments(action_node, 1)
            answer_node = create_structure(node)

            self.find_college(node, answer_node)
            self.finish_agent(action_node, answer_node)

            _logger.debug("SearchUCollegeByRegionAgent ends")
        except Exception as ex:
            self.set_unsuccessful_status(action_node)
            status = ScResult.ERROR
        finally:
            create_edge(
                sc_types.EDGE_ACCESS_CONST_POS_PERM,
                self._keynodes['question_finished'],
                action_node,
            )
        return status

    def find_college(self, college_region: ScAddr, answer_node: ScAddr) -> None:
        college_template = ScTemplate()
        college_template.triple_with_relation(
            [sc_types.UNKNOWN, "_college"],
            sc_types.EDGE_D_COMMON_VAR,
            [college_region, "_region_node"],
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            self._keynodes["nrel_region"]
        )
        _logger.debug("1st passed")
        college_template.triple(
            self._keynodes['concept_college'],
            [sc_types.EDGE_ACCESS_VAR_POS_PERM, "_edge_to_college"],
            "_college"
        )
        _logger.debug("2st passed")
        result = client.template_search(college_template)
        wrap_in_set(answer_node, self._keynodes['concept_college'])

        for item in result:
            _logger.debug("SearchCollegeByRegionAgent get answer: " +
                          get_system_idtf(item.get(0)))

            wrap_in_set(answer_node, item.get(1), item.get(0))

        wrap_in_set(answer_node, self._keynodes['concept_college'])

    def set_unsuccessful_status(self, action_node: ScAddr) -> None:
        create_edge(
            sc_types.EDGE_ACCESS_CONST_POS_PERM,
            self._keynodes['question_finished_unsuccessfully'],
            action_node,
        )

    def finish_agent(self, action_node: ScAddr, answer: ScAddr) -> None:
        contour_edge = create_edge(
            sc_types.EDGE_D_COMMON_CONST,
            action_node,
            answer,
        )
        create_edge(
            sc_types.EDGE_ACCESS_CONST_POS_PERM,
            self._keynodes['nrel_answer'],
            contour_edge,
        )
        create_edge(
            sc_types.EDGE_ACCESS_CONST_POS_PERM,
            self._keynodes['question_finished_successfully'],
            action_node,
        )