import kgcl.diff.diff_2_kgcl_triple_annotation as annotation
import rdflib
from datetime import datetime
from kgcl.diff.pretty_print_kgcl import render_instances
import kgcl.diff.diff_2_kgcl_single as single
import kgcl.diff.diff_2_kgcl_existential as existential
import os
from rdflib.util import guess_format


def ts():
    now = datetime.now()
    dt_string = now.strftime("%H:%M:%S ")
    return dt_string


def run(ingraph, outgraph, output):

    os.mkdir(output)

    # load graphs
    g1 = rdflib.Graph()
    g2 = rdflib.Graph()
    # g1.parse(ingraph)
    g1.load(ingraph, format=guess_format(ingraph))
    print(ts() + "Loaded Graph 1")
    # g2.parse(outgraph)
    g2.load(outgraph, format=guess_format(outgraph))
    print(ts() + "Loaded Graph 2")

    # compute diff
    existential_summary = existential.generate_atomic_existential_commands(g1, g2)
    print(ts() + "Generated Diff for Existentials")
    triple_annotation_summary = annotation.generate_triple_annotation_commands(g1, g2)
    print(ts() + "Generated Diff for Triple Annotations")
    single_triple_summary = single.generate_thin_triple_commands(g1, g2)
    print(ts() + "Generated Diff for Thin Triples")

    # write summary report
    with open(output + "/kgcl_summary.txt", "w") as f:
        f.write(existential_summary.get_summary_KGCL_commands())
        f.write(triple_annotation_summary.get_summary_KGCL_commands())
        f.write(single_triple_summary.get_summary_KGCL_commands())

    # write non-deterministic diff report
    nd_node_moves = single_triple_summary.get_non_deterministic_node_moves()
    nd_predicate_changes = (
        single_triple_summary.get_non_deterministic_predicate_changes()
    )
    nd_renamings = single_triple_summary.get_non_deterministic_renamings()

    non_deterministic_folder = os.path.join(output, "non_deterministic")
    os.mkdir(non_deterministic_folder)
    with open(non_deterministic_folder + "/node_moves.txt", "w") as f:
        f.write(render_non_deterministic_diff(nd_node_moves))
    with open(non_deterministic_folder + "/predicate_changes.txt", "w") as f:
        f.write(render_non_deterministic_diff(nd_predicate_changes))
    with open(non_deterministic_folder + "/renamings.txt", "w") as f:
        f.write(render_non_deterministic_diff(nd_renamings))

    # get KGCL commands
    kgcl_commands = existential_summary.get_commands()
    kgcl_commands += triple_annotation_summary.get_commands()
    kgcl_commands += single_triple_summary.get_commands()

    # write KGCL commands
    with open(output + "/patch.kgcl", "w") as f:
        for k in kgcl_commands:
            f.write(k)
            f.write("\n")

    # write distinct KGCL commands
    patch_folder = os.path.join(output, "patch")
    os.mkdir(patch_folder)

    with open(patch_folder + "/existential_additions.txt", "w") as f:
        for k in existential_summary.get_existential_additions():
            f.write(k)
            f.write("\n")

    with open(patch_folder + "/existential_deletions.txt", "w") as f:
        for k in existential_summary.get_existential_deletions():
            f.write(k)
            f.write("\n")

    with open(patch_folder + "/triple_annotation_additions.txt", "w") as f:
        for k in triple_annotation_summary.get_triple_annotation_additions():
            f.write(k)
            f.write("\n")

    with open(patch_folder + "/triple_annotation_deletions.txt", "w") as f:
        for k in triple_annotation_summary.get_triple_annotation_deletions():
            f.write(k)
            f.write("\n")

    with open(patch_folder + "/renamings.txt", "w") as f:
        for k in single_triple_summary.get_renamings():
            f.write(k)
            f.write("\n")

    with open(patch_folder + "/class_creations.txt", "w") as f:
        for k in single_triple_summary.get_class_creations():
            f.write(k)
            f.write("\n")

    with open(patch_folder + "/subsumption_creations.txt", "w") as f:
        for k in single_triple_summary.get_subsumption_creations():
            f.write(k)
            f.write("\n")

    with open(patch_folder + "/subsumption_deletions.txt", "w") as f:
        for k in single_triple_summary.get_subsumption_deletions():
            f.write(k)
            f.write("\n")

    with open(patch_folder + "/predicate_changes.txt", "w") as f:
        for k in single_triple_summary.get_predicate_changes():
            f.write(k)
            f.write("\n")

    with open(patch_folder + "/node_moves.txt", "w") as f:
        for k in single_triple_summary.get_node_moves():
            f.write(k)
            f.write("\n")

    with open(patch_folder + "/synonym_creations.txt", "w") as f:
        for k in single_triple_summary.get_synonym_creations():
            f.write(k)
            f.write("\n")

    with open(patch_folder + "/edge_creations.txt", "w") as f:
        for k in single_triple_summary.get_edge_creations():
            f.write(k)
            f.write("\n")

    with open(patch_folder + "/edge_deletions.txt", "w") as f:
        for k in single_triple_summary.get_edge_deletions():
            f.write(k)
            f.write("\n")

    pp_kgcl_commands = render_instances(kgcl_commands, g1)
    with open(output + "/pp_patch.kgcl", "w") as f:
        for a in pp_kgcl_commands:
            f.write(a)
            f.write("\n")


# a non-deterministic diff consists of a list of tuples.
# A tuple contains two sets of triples that are involved in the non-deterministic diff
def render_non_deterministic_diff(nd):
    out = ""
    for tuple in nd:
        from_triples = tuple[0]
        to_triples = tuple[1]
        rendering = ""
        for s, p, o in from_triples:
            triple = " (" + str(s) + "," + str(p) + "," + str(o) + ")\n"
            rendering += triple
        rendering += "->\n"
        for s, p, o in to_triples:
            triple = " (" + str(s) + "," + str(p) + "," + str(o) + ")\n"
            rendering += triple

        out += rendering + "\n\n"

    return out
