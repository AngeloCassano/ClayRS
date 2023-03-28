import explanation
import explanation_generator
from clayrs.recsys import NXFullGraph, ItemNode, PropertyNode, NXPageRank, TestRatingsMethodology
from clayrs.recsys.explanation_generator import generate_explanation

G, sorted_prop, profile, recommendations= explanation.explain(["I:11033","I:8360","I:1661","I:8487"], ["I:11768","I:69"]) #,"I:69"
triple_structure = explanation_generator.build_triple_structure(G, sorted_prop, profile, recommendations)
print(triple_structure)
print()
explanation = generate_explanation(triple_structure, recommendations, profile, G, "primolivello",1,False)
print(explanation)