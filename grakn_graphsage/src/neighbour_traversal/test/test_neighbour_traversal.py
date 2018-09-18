

import unittest
# from parameterized import parameterized
from ddt import ddt, data

import grakn
from grakn.service.Session.Concept.Concept import Concept, Role

from grakn_graphsage.src.neighbour_traversal.neighbour_traversal import build_neighbourhood_generator, NeighbourRole, \
    ConceptWithNeighbourhood, NEIGHBOUR_PLAYS, TARGET_PLAYS, collect_to_tree, UNKNOWN_ROLE_TARGET_PLAYS, \
    UNKNOWN_ROLE_NEIGHBOUR_PLAYS

client = grakn.Grakn(uri="localhost:48555")
session = client.session(keyspace="test_schema")

@ddt
class TestNeighbourTraversalFromEntity(unittest.TestCase):
    def setUp(self):
        self.tx = session.transaction(grakn.TxType.WRITE)

        # identifier = "Jacob J. Niesz"
        # entity_query = "match $x isa person, has identifier '{}'; get $x;".format(identifier)
        entity_query = "match $x isa person, has name 'Sundar Pichai'; get;"

        self._concept = list(self.tx.query(entity_query))[0].get('x')

    def tearDown(self):
        self.tx.close()

    def _assert_types_correct(self, concept_with_neighbourhood):
        """
        Check that all of the types in the structure are as expected
        :param concept_with_neighbourhood:
        :return:
        """
        self.assertTrue(isinstance(concept_with_neighbourhood, ConceptWithNeighbourhood))
        self.assertTrue(isinstance(concept_with_neighbourhood.concept, Concept))

        self.assertTrue(type(concept_with_neighbourhood.neighbourhood).__name__ in ('generator', 'chain'))

        neighbour_role = next(concept_with_neighbourhood.neighbourhood, None)
        if neighbour_role is not None:
            self.assertTrue(isinstance(neighbour_role, NeighbourRole))

            self.assertTrue(isinstance(neighbour_role.role, Role) or neighbour_role.role in [UNKNOWN_ROLE_TARGET_PLAYS,
                                                                                             UNKNOWN_ROLE_NEIGHBOUR_PLAYS])
            self.assertIn(neighbour_role.target_or_neighbour_plays, [TARGET_PLAYS, NEIGHBOUR_PLAYS])
            self.assertTrue(self._assert_types_correct(neighbour_role.neighbour))

        return True

    def _assert_depth_correct(self, concept_with_neighbourhood):
        neighbour_role = next(concept_with_neighbourhood.neighbourhood, None)
        if neighbour_role is not None:
            self._assert_depth_correct(neighbour_role.neighbour)

    @data(1, 2, 3)
    def test_neighbour_traversal_structure_types(self, k):
        self._concept_with_neighbourhood = build_neighbourhood_generator(self.tx, self._concept, k)
        self._assert_types_correct(self._concept_with_neighbourhood)

    @data(1, 2, 3)
    def test_neighbour_traversal_check_depth(self, k):
        # k = 1
        self._concept_with_neighbourhood = build_neighbourhood_generator(self.tx, self._concept, k)

        collected_tree = collect_to_tree(self._concept_with_neighbourhood)
        self.assertEqual(len(collected_tree.neighbourhood), 2)
        # self._assert_depth_correct(self._concept_with_neighbourhood)
