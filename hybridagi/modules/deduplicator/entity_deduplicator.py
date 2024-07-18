import dspy
from enum import Enum
from typing import Optional, Union
from hybridagi.embeddings.embeddings import Embeddings
from hybridagi.core.datatypes import EntityList, FactList

class Method(str, Enum):
    ExactMatch: str = "exact_match"
    Embeddings: str = "embeddings"
    Fuzzy: str = "fuzzy"
    
class EmbeddingsDistance(str, Enum):
    Cosine = "cosine"
    Euclidean = "euclidean"
    
class FuzzyDistance(str, Enum):
    TokenSort = "token_sort"
    PartialRatio = "partial_ratio"
    SimpleRatio = "simple_ratio"

class EntityDeduplicator(dspy.Module):
    
    def __init__(
            self,
            method: str = "exact_match",
            embeddings: Optional[Embeddings] = None,
            embeddings_distance: Optional[str] = None,
            fuzzy_distance: Optional[str] = None,
            max_distance: float = 0.7,
        ):
        if method != Method.ExactMatch and method != Method.Embeddings and method != Method.Fuzzy:
            raise ValueError(f"Invalid method for {type(self).__name__} should be exact_match or embeddings or fuzzy")
        if method == Method.Embeddings:
            if embeddings_distance is None:
                raise ValueError(f"Embeddings distance not provided for {type(self).__name__} should be cosine or eucliean")
            if embeddings is None:
                raise ValueError(f"Embeddings not provided for {type(self).__name__}")
        if method ==  Method.Fuzzy:
            if fuzzy_distance is None:
                raise ValueError(f"Fuzzy distance not provided for {type(self).__name__} should be token_sort or partial_ratio or simple_ratio.")
            if fuzzy_distance != FuzzyDistance.TokenSort and fuzzy_distance != FuzzyDistance.PartialRatio and fuzzy_distance != FuzzyDistance.SimpleRatio:
                raise ValueError(f"Invalid fuzzy distance for {type(self).__name__} should be token_sort or partial_ratio or simple_ratio.")
        self.method = method
        self.embeddings = embeddings
        self.embeddings_distance = embeddings_distance
        self.fuzzy_distance = fuzzy_distance
        self.max_distance = max_distance
    
    def forward(self, entities_or_facts: Union[EntityList, FactList]) -> Union[EntityList, FactList]:
        if self.method == Method.ExactMatch:
            if isinstance(entities_or_facts, EntityList):
                entity_map = {}
                result = EntityList()
                for ent in entities_or_facts.entities:
                    # make the matching case insensitive
                    entity_name_and_label = ent.name.lower() + ent.label.lower()
                    if entity_name_and_label not in entity_map:
                        entity_map[entity_name_and_label] = ent
                        result.entities.append(ent)
                return result
            elif isinstance(entities_or_facts, FactList):
                entity_map = {}
                result = FactList()
                for fact in entities_or_facts.facts:
                    # make the matching case insensitive
                    subject_name_and_label = fact.subj.name.lower() + fact.subj.label.lower()
                    object_name_and_label = fact.obj.name.lower() + fact.obj.label.lower()
                    if subject_name_and_label not in entity_map:
                        entity_map[subject_name_and_label] = fact.subj
                    else:
                        fact.subj = entity_map[subject_name_and_label]
                    if object_name_and_label not in entity_map:
                        entity_map[object_name_and_label] = fact.obj
                    else:
                        fact.obj = entity_map[object_name_and_label]
                    result.facts.append(fact)
                return result
            else:
                raise ValueError(f"Invalid input for {type(self).__name__} should be EntityList or FactList")
        elif self.method == Method.Fuzzy:
            raise NotImplementedError(f"Fuzzy matching for {type(self).__name__} not implemented yet.")
        elif self.method == Method.Embeddings:
            raise NotImplementedError(f"Embeddings matching for {type(self).__name__} not implemented yet.")
        
        
                