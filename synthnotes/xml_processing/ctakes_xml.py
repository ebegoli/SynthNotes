from lxml import etree
import os
from uuid import uuid4
from typing import Dict

from typing import Dict, List, Optional, Iterator


def contains(e1: Dict, e2: Dict) -> bool:
    return e1['begin'] <= e2['begin'] and e1['end'] >= e2['end']


class CtakesXmlOutput(object):
    """ Contains methods for retrieving elements from xml output """

    def __init__(self, file: str) -> None:
        self.tree = etree.parse(file)
        self.root = self.tree.getroot()
        self.nsmap = self.root.nsmap
        self.doc_id = self._get_doc_id()

    def _get_doc_id(self) -> int:
        doc_id_elem = self.tree.find('structured:DocumentID',
                                     namespaces=self.nsmap)
        doc_id = doc_id_elem.attrib.get('documentID')
        return int(doc_id)

    @property
    def sentences(self) -> Iterator[etree.Element]:
        return self.tree.iterfind('textspan:Sentence', namespaces=self.nsmap)

    @property
    def tokens(self) -> Iterator[etree.Element]:
        syntax_elems = self.tree.iterfind('syntax:*', namespaces=self.nsmap)
        tokens = (e for e in syntax_elems if e.tag.endswith('Token'))
        return tokens

    @property
    def chunks(self) -> Iterator[etree.Element]:
        return self.tree.iterfind('syntax:Chunk', namespaces=self.nsmap)

    @property
    def mentions(self) -> Iterator[etree.Element]:
        syntax_elems = self.tree.iterfind('textsem:*', namespaces=self.nsmap)
        mentions = (e for e in syntax_elems if e.tag.endswith('Mention'))
        return mentions

    @property
    def annotations(self) -> Iterator[etree.Element]:
        syntax_elems = self.tree.iterfind('textsem:*', namespaces=self.nsmap)
        annotations = (e for e in syntax_elems if e.tag.endswith('Annotation'))
        return annotations

    @property
    def dependencies(self) -> Iterator[etree.Element]:
        return self.tree.iterfind('syntax:ConllDependencyNode', namespaces=self.nsmap)

    @property
    def predicates(self) -> Iterator[etree.Element]:
        return self.tree.iterfind('textsem:Predicate', namespaces=self.nsmap)

    @property
    def semantic_args(self) -> Iterator[etree.Element]:
        return self.tree.iterfind('textsem:SemanticArgument', namespaces=self.nsmap)

    @property
    def semantic_roles(self) -> Iterator[etree.Element]:
        return self.tree.iterfind('textsem:SemanticRoleRelation', namespaces=self.nsmap)

    @property
    def nonempty_fs(self) -> Iterator[etree.Element]:
        return self.tree.iterfind('cas:NonEmptyFSList', namespaces=self.nsmap)

    @property
    def umls_concepts(self) -> Iterator[etree.Element]:
        return self.tree.iterfind('refsem:UmlsConcept', namespaces=self.nsmap)

class RowFactory(object):
    def __init__(self):
        self.keys = {
            ('id',''),
            ('sent_id', ''),
            ('elem_type', ''),
            ('doc_id', 0),
            ('begin', 0 ),
            ('end', 0),
            ('sentence_number', 0),
            ('xmi_id', 0),
            ('pos', ''),
            ('canonical_form', ''),
            ('numpos', 0),
            ('token_type', ''),
            ('chunk_type', ''),
            ('mention_type', ''),
            ('ontology_arr', ''),
            ('discovery_technique', 0),
            ('polarity', 0),
            ('conditional', False),
            ('generic', False),
            ('history_of', 0),
            ('subject', ''),
            ('dep_id', ''),
            ('form', ''),
            ('lemma', ''),
            ('cpostag', ''),
            ('postag', ''),
            ('feats', ''),
            ('deprel', ''),
            ('pdeprel', ''),
            ('head', 0),
            ('relations', ''),
            ('frameset', ''),
            ('relation', 0),
            ('label', ''),
            ('predicate', 0),
            ('argument', 0),
            ('code', ''),
            ('disambiguated', False),
            ('cui', ''),
            ('tui', ''),
            ('preferred_text',''),
            ('coding_scheme', ''),
            ('annotation_type', '')
        }

    def get_dict(self, d):   
        self_dict = {}
        for k, default_val in self.keys:
            self_dict[k] = default_val

        self_dict.update(d)
        return self_dict

class CtakesXmlParser(object):
    """ Parse ctakes xml output """
    def __init__(self, columnar=False):
        self.row_factory = RowFactory()
        self.columnar = columnar

    def parse(self, file_name) -> List:
        """ Takes filename of a ctakes xml output file and returns list of dictionaries which contain xml elements """
        xmlout: CtakesXmlOutput = CtakesXmlOutput(file_name)

        result = None
        if self.columnar:
            result = []
        else:
            result = {}

        doc_id: int = xmlout.doc_id
        # result['doc_id'] = doc_id

        sentences = self.get_sents(xmlout.sentences, doc_id)
        # result.extend(sentences)
        self._store_elements_list(sentences, 'sentences', result)
        # self.write(sentences, CtakesOrm.Sentence)

        self._store_elements_list(self.get_tokens(xmlout.tokens, doc_id, sentences),
                                  'tokens', result)

        # result.extend(self.get_chunks(xmlout.chunks, doc_id, sentences))
        
        self._store_elements_list(self.get_mentions(xmlout.mentions, doc_id, sentences),
                                 'mentions', result)
       
        self._store_elements_list(self.get_annotations(xmlout.annotations, doc_id, sentences),
                                    'annotations', result)

        # result.extend(self.get_dependencies(xmlout.dependencies, doc_id, sentences))
        # self.write(self.get_dependencies(xmlout.dependencies, doc_id, sentences),
        #            CtakesOrm.ConllDependency)
        #
        self._store_elements_list(self.get_predicates(xmlout.predicates, doc_id, sentences),
                                    'predicates', result)
                
        # result.extend(self.get_sem_args(xmlout.semantic_args, doc_id, sentences))
        
        # result.extend(self.get_sem_roles(xmlout.semantic_roles, doc_id))
                        
        self._store_elements_list(self.get_umls(xmlout.umls_concepts, doc_id),
                                    'umls_concepts', result)
        # self.write(self.get_umls(xmlout.umls_concepts, doc_id),
        #            CtakesOrm.UMLSConcept)
        return result

    def get_sents(self, sents: Iterator[etree.Element], doc_id: int) -> List[Dict]:
        db_sents = []
        for s in sents:
            d = {
                'id': str(uuid4()),
                'elem_type': 'Sentence',
                'doc_id': doc_id,
                'begin': int(s.attrib.get('begin', 0)),
                'end': int(s.attrib.get('end', 0)),
                'sentence_number': int(s.attrib.get('sentenceNumber', 0)),
                'xmi_id': int(s.attrib.get('{http://www.omg.org/XMI}id', 0))
            }
            db_sents.append(self._get_storage_format(d))
        return db_sents

    def get_tokens(self, tokens: Iterator[etree.Element], doc_id: int,
                   sentences: List[Dict]) -> Iterator[Dict]:

        for t in tokens:
            d = {
                'id': str(uuid4()),
                'elem_type': 'Token',                
                'doc_id': doc_id,
                'begin': int(t.attrib.get('begin', 0)),
                'end': int(t.attrib.get('end', 0)),
                'xmi_id': self.get_xmi_id(t),
                'pos': t.attrib.get('partOfSpeech', ''),  # newlines don't have pos
                'canonical_form': t.attrib.get('canonical_form', ''),
                'numpos': int(t.attrib.get('numPosition', 0)),
                'token_type': t.tag.split('}')[1]
            }
            self.set_sent_id(d, sentences)
            yield self._get_storage_format(d)

    def get_chunks(self, chunks, doc_id, sentences):

        for c in chunks:
            d = {
                'id': str(uuid4()),
                'elem_type': 'Chunk',
                'doc_id': doc_id,
                'xmi_id': self.get_xmi_id(c),
                'begin': int(c.attrib.get('begin', 0)),
                'end': int(c.attrib.get('end', 0)),
                'chunk_type': c.attrib.get('chunkType')
            }
            # chunk = CtakesOrm.Chunk(**d)
            self.set_sent_id(d, sentences)

            yield self._get_storage_format(d)

    def get_mentions(self, mentions, doc_id, sentences):

        for elem in mentions:
            d = {
                'id': str(uuid4()),
                'elem_type': 'Mention',
                'doc_id': doc_id,
                'xmi_id': self.get_xmi_id(elem),
                'begin': int(elem.attrib.get('begin', 0)),
                'end': int(elem.attrib.get('end', 0)),
                'mention_type': elem.tag.split('}')[1],
                # There is a bug in parquet that won't take empty lists.
                'ontology_arr': elem.attrib.get('ontologyConceptArr', ''),                  
                'discovery_technique': int(elem.attrib.get('discoveryTechnique', 0)),
                'polarity': int(elem.attrib.get('polarity', 0)),
                'conditional': elem.attrib.get('conditional') == 'true',
                'generic': elem.attrib.get('generic') == 'true',
                'history_of': int(elem.attrib.get('historyOf', 0)),
                'subject': elem.attrib.get('subject')
            }

            self.set_sent_id(d, sentences)

            yield self._get_storage_format(d)

    def get_annotations(self, annotations, doc_id, sentences):

        for elem in annotations:
            d = {
                'id': str(uuid4()),
                'elem_type': 'Annotation',
                'doc_id': doc_id,
                'xmi_id': self.get_xmi_id(elem),
                'begin': int(elem.attrib.get('begin', 0)),
                'end': int(elem.attrib.get('end', 0)),
                'annotation_type': elem.tag.split('}')[1],
                'discovery_technique': int(elem.attrib.get('discoveryTechnique', 0)),
                'polarity': int(elem.attrib.get('polarity', 0)),
                'conditional': elem.attrib.get('conditional') == 'true',
                'generic': elem.attrib.get('generic') == 'true',
                'history_of': int(elem.attrib.get('historyOf', 0)),
            }
            self.set_sent_id(d, sentences)
            yield self._get_storage_format(d)

    def get_dependencies(self, deps, doc_id, sentences):

        for elem in deps:
            d = {
                'id': str(uuid4()),
                'elem_type': 'Dependency',
                'doc_id': doc_id,
                'xmi_id': self.get_xmi_id(elem),
                'begin': int(elem.attrib.get('begin', 0)),
                'end': int(elem.attrib.get('end', 0)),
                'dep_id': elem.attrib.get('id'),
                'form': elem.attrib.get('form', ''),
                'lemma': elem.attrib.get('lemma', ''),
                'cpostag': elem.attrib.get('cpostag', ''),
                'postag': elem.attrib.get('postag', ''),
                'feats': elem.attrib.get('feats', ''),
                'deprel': elem.attrib.get('deprel', ''),
                'pdeprel': elem.attrib.get('pdeprel', ''),
                'head': int(elem.attrib.get('head', '0'))
            }

            self.set_sent_id(d, sentences)
            yield self._get_storage_format(d)

    def get_predicates(self, preds, doc_id, sentences):

        for elem in preds:
            d = {
                'id': str(uuid4()),
                'elem_type': 'Predicate',
                'doc_id': doc_id,
                'xmi_id': self.get_xmi_id(elem),
                'begin': int(elem.attrib.get('begin', 0)),
                'end': int(elem.attrib.get('end', 0)),
                # There is a bug in parquet that won't take empty lists.
                'relations': elem.attrib.get('relations', ''),
                'frameset': elem.attrib.get('frameSet')
            }

            self.set_sent_id(d, sentences)
            yield self._get_storage_format(d)

    def get_sem_args(self, args, doc_id, sentences):

        for elem in args:
            d = {
                'id': str(uuid4()),
                'elem_type': 'SemanticArg',
                'doc_id': doc_id,
                'xmi_id': self.get_xmi_id(elem),
                'begin': int(elem.attrib.get('begin', 0)),
                'end': int(elem.attrib.get('end', 0)),
                'relation': int(elem.attrib.get('relation', 0)),
                'label': elem.attrib.get('label')
            }

            self.set_sent_id(d, sentences)
            yield self._get_storage_format(d)

    def get_sem_roles(self, roles, doc_id):

        for elem in roles:
            d = {
                'id': str(uuid4()),
                'elem_type': 'SemanticRole',
                'doc_id': doc_id,
                'xmi_id': self.get_xmi_id(elem),
                'discovery_technique': int(elem.attrib.get('discoveryTechnique', 0)),
                'polarity': int(elem.attrib.get('polarity', 0)),
                'conditional': elem.attrib.get('conditional') == 'true',
                'predicate': int(elem.attrib.get('predicate', 0)),
                'argument': int(elem.attrib.get('argument', 0))
            }
            yield self._get_storage_format(d)

    def get_fs_list(self, fs_list, doc_id):

        for elem in fs_list:
            d = {
                'id': str(uuid4()),
                'elem_type': 'FSList',
                'doc_id': doc_id,
                'xmi_id': self.get_xmi_id(elem),
                'head': int(elem.attrib.get('head', 0)),
                'tail': int(elem.attrib.get('tail', 0))
            }

        yield self._get_storage_format(d)

    def get_umls(self, umls_list, doc_id):

        for elem in umls_list:
            d = {
                'id': str(uuid4()),
                'elem_type': 'UmlsConcept',
                'doc_id': doc_id,
                'xmi_id': self.get_xmi_id(elem),
                'coding_scheme': elem.attrib.get('codingScheme'),
                'code': elem.attrib.get('code', ''),
                'disambiguated': elem.attrib.get('disambiguated') == 'true',
                'cui': elem.attrib.get('cui'),
                'tui': elem.attrib.get('tui'),
                'preferred_text': elem.attrib.get('preferredText')
            }

            yield self._get_storage_format(d)

    def get_xmi_id(self, elem: etree.Element) -> int:
        return int(elem.get('{http://www.omg.org/XMI}id'))

    def set_sent_id(self, d: Dict, sentences: List[Dict]):
        sent_id = self._get_containing_sentence(d, sentences)
        if sent_id is not None:
            d['sent_id'] = sent_id

    def _get_containing_sentence(self, elem: Dict, sentences: List[Dict]) -> Optional[int]:
        for s in sentences:
            if contains(s, elem):
                return s['id']
        return None

    def _get_storage_format(self, elem_dict: Dict):
        if self.columnar:
            return self.row_factory.get_dict(elem_dict)
        else:
            return elem_dict

    def _store_elements_list(self, elem_list, elem_type, results):
        if self.columnar:
            results.append(elem_list)

        else:
            results[elem_type] = elem_list

