

import unittest

import grakn

from grakn_graphsage.src.neighbour_traversal.neighbour_traversal import traverse_neighbours


class TestNeighbourTraversal(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_neighbour_traversal(self):
        client = grakn.Grakn(uri="localhost:48555")
        session = client.session(keyspace="genealogy")
        tx = session.transaction(grakn.TxType.WRITE)

        # concept = list(tx.query("match $x isa person, has firstname {}, has surname {}; get $x;".format("Jacob",
        # "Young")))[0]

        identifier = "Jacob J. Niesz"
        concept = list(tx.query("match $x isa person, has identifier '{}'; get $x;".format(identifier)))[0].get('x')

        concept_id = concept.id

        neighbour_info = traverse_neighbours(tx, concept, 2)

        roles_played = [role_played for role_played in neighbour_info['roles_played']]
        roleplayers = [roleplayer for roleplayer in neighbour_info['roleplayers']]
        tx.close()
