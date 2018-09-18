

import unittest

import grakn
from grakn.service.Session.Concept.Concept import Concept, Role

from grakn_graphsage.src.neighbour_traversal.neighbour_traversal import build_neighbourhood_generator, NeighbourRole, \
    ConceptWithNeighbourhood, NEIGHBOUR_PLAYS, TARGET_PLAYS


class TestNeighbourTraversalFromEntity(unittest.TestCase):
    def setUp(self):
        self._client = grakn.Grakn(uri="localhost:48555")
        self._session = self._client.session(keyspace="genealogy")

    def tearDown(self):
        pass

    def _assert_type_instances_correct(self, concept_with_neighbourhood):
        self.assertTrue(isinstance(concept_with_neighbourhood, ConceptWithNeighbourhood))
        self.assertTrue(isinstance(concept_with_neighbourhood.concept, Concept))

        self.assertTrue(type(concept_with_neighbourhood.neighbourhood).__name__ == 'generator')

        neighbour_role = next(concept_with_neighbourhood.neighbourhood)
        if neighbour_role:
            self.assertTrue(isinstance(neighbour_role, NeighbourRole))

            self.assertTrue(isinstance(neighbour_role.role, Role) or neighbour_role.role == 'UNKNOWN_ROLE')
            self.assertIn(neighbour_role.target_or_neighbour_plays, [TARGET_PLAYS, NEIGHBOUR_PLAYS])
            self.assertTrue(self._assert_type_instances_correct(neighbour_role.neighbour))
        return True

    def test_neighbour_traversal_structure(self):

        tx = self._session.transaction(grakn.TxType.WRITE)

        # concept = list(tx.query("match $x isa person, has firstname {}, has surname {}; get $x;".format("Jacob",
        # "Young")))[0]

        identifier = "Jacob J. Niesz"
        concept = list(tx.query("match $x isa person, has identifier '{}'; get $x;".format(identifier)))[0].get('x')

        concept_with_neighbourhood = build_neighbourhood_generator(tx, concept, 2)

        self._assert_type_instances_correct(concept_with_neighbourhood)

        # neighbour_roles = [neighbour_role for neighbour_role in concept_with_neighbourhood.neighbourhood]

        tx.close()
