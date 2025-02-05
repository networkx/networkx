"""
Function to find vertex cover of size atmost k
"""

from networkx.utils.decorators import not_implemented_for

preprocessing_rules = []


@not_implemented_for("directed")
def vertex_cover_preprocessing(G, k, vc):
    while k > 0:
        applied = False

        for rule in preprocessing_rules:
            if not applied:
                applied, G, k, to_remove_from_vc, to_add_to_vc, is_k_vc_possible = rule(
                    G, k, vc
                )

                if not is_k_vc_possible:
                    # vc of size atmost k not possible
                    return False

                if to_remove_from_vc:
                    assert isinstance(vc, set)
                    vc.difference_update(to_remove_from_vc)
                if to_add_to_vc:
                    vc.update(to_add_to_vc)

        if not applied:
            break

    if k <= 0 and len(G.edges):
        return False

    return True
