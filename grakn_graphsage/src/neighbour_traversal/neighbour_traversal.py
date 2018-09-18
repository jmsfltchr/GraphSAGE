from collections import namedtuple

import grakn


NeighbourRole = namedtuple('NeighbourRole', ['role', 'neighbour'])
ConceptWithNeighbourhood = namedtuple('ConceptWithNeighbourhood', ['concept', 'neighbourhood'])
Neighbourhood = namedtuple('Neighbourhood', ['roleplayers', 'roles_played'])


def build_neighbourhood_generator(grakn_tx: grakn.Transaction,
                                  target_concept: grakn.service.Session.Concept.Concept,
                                  depth: int):

    if depth == 0:
        # # This marks the end of the recursion, simply return this concept
        # return target_concept
        return None

    def _empty():
        yield from ()

    neighbourhood = Neighbourhood(roleplayers=_empty(), roles_played=_empty())

    # Different cases for traversal

    # Any concept could play a role in a relationship if the schema permits it
    # TODO Inferred concepts have an id, but can we treat them exactly the same as non-inferred, or must we keep the
    # transaction open?
    node_id = target_concept.id

    # TODO Can't do this presently since querying for the role throws an exception
    # roles_played_iterator = grakn_tx.query("match $x id {}; $relationship($role: $x); get $relationship,
    # $role;".format(node_id))
    roles_played_iterator = grakn_tx.query("match $x id {}; $relationship($x); get $relationship;".format(node_id))

    def _get_role_and_relationship():
        for answer in roles_played_iterator:
            # TODO See above, omitting due to bug
            # role_concept = answer.get("role")
            role_concept = "UNKNOWN_ROLE"
            relationship_concept = answer.get("relationship")
            yield {'role:': role_concept,
                   'concept': relationship_concept,
                   'neighbours': build_neighbourhood_generator(grakn_tx, relationship_concept, depth - 1)}

    # Distinguish the concepts found as roles-played
    # Get them lazily
    neighbourhood.roles_played = _get_role_and_relationship()

    # if node.is_entity():
    #     # Nothing special to do here?
    #     pass
    if target_concept.is_attribute():
        # Do anything specific to attribute values
        # Optionally stop further propagation through attributes, since they are shared across the knowledge graph so
        # this may not provide relevant information
        neighbourhood.value = target_concept.value()
    elif target_concept.is_relationship():
        # Find it's roleplayers
        # id and rel_type should be known (providing rel_type speeds up the query, but shouldn't since we provide the
        #  id)
        # Then from this list of roleplayers, remove `node`, since that's where we've come from
        # Distinguish the concepts found as roleplayers

        roleplayers_iterator = grakn_tx.query(
            "match $relationship id {}; $relationship($role: $x) isa {}; get $x, $role;".format(node_id,
                                                                                                target_concept.type().label()))

        def _get_roleplayers():
            for answer in roleplayers_iterator:
                role_concept = answer.get("role")
                roleplayer_concept = answer.get("x")

                neighbour = ConceptWithNeighbourhood(concept=roleplayer_concept,
                                                     neighbourhood=build_neighbourhood_generator(grakn_tx, roleplayer_concept,
                                                                                  depth - 1))
                yield NeighbourRole(role=role_concept, neighbour=neighbour)

        neighbourhood.roleplayers = _get_roleplayers()

    return ConceptWithNeighbourhood(concept=target_concept, neighbourhood=neighbourhood)

# def walk_for_aggregate(target_node, neighbour_graph):
#     neighbour_graph


def traverse(concept_with_neighbourhood):

    # concept_with_neighbourhood.neighbourhood = {n for n in concept_with_neighbourhood.neighbourhood}

    neighbourhood = concept_with_neighbourhood.neighbourhood

    neighbourhood.roles_played = {neighbour_role_played for neighbour_role_played in neighbourhood.roles_played}

    [traverse(neighbour_role_played.neighbour) for neighbour_role_played in neighbourhood.roles_played]

    # roles_played = set()
    # for neighbour_role_played in neighbourhood.roles_played:
    #     roles_played.add(neighbour_role_played)
    #     traverse(neighbour_role_played.neighbour)

    neighbourhood.roleplayers = {neighbour_roleplayer for neighbour_roleplayer in neighbourhood.roleplayers}

    return concept_with_neighbourhood


def generate_neighbour_trees(neighbourhood_generator):
    """
    Given the neighbour generators, yield the fully populated tree of each of the target concept's neighbours
    :param neighbourhood_generators:
    :return:
    """

    for neighbourhood in neighbourhood_generator:
        roles_played = [role_played for role_played in neighbourhood.roles_played]
