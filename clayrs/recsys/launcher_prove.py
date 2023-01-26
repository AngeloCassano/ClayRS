import explanation
import explaination_generator
from clayrs.recsys import NXFullGraph, ItemNode, PropertyNode, NXPageRank, TestRatingsMethodology

G, sorted_prop, profile, recommendations= explanation.explain(["I:11033","I:8360","I:1661","I:8487"], ["I:11768","I:69"])
triple_structure = explaination_generator.build_triple_structure(G, sorted_prop, profile, recommendations)
print(triple_structure)