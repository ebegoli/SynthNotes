import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
from fastparquet import ParquetFile
import os
from stringdist import levenshtein_norm as lev_norm



class Preprocessor(object):
    def __init__(self, pq_file_dir, output, mimic_notes):
        self.pq_file_dir = pq_file_dir
        self.output = output
        self.mimic_notes_file = mimic_notes

        pf = ParquetFile(self.mimic_notes_file)
        self.notes = pf.to_pandas()    

        self.preds = self.get_df_from_pq(self.pq_file_dir, 'predicates')
        self.mentions = self.get_df_from_pq(self.pq_file_dir, 'mentions')
        self.umls = self.get_df_from_pq(self.pq_file_dir, 'umls_concepts')
        self.sents = self.get_df_from_pq(self.pq_file_dir, 'sentences')
        print("Finished loading data...")
        
    def preprocess(self):
        self.sents = self.sents.rename({'id': 'sent_id'}, axis=1)

        # Add raw text from notes to sentences
        self.sents = self.sents.rename({'id': 'sent_id'}, axis=1)
        self.sents = self.sents.merge(self.notes[['ROW_ID', 'TEXT']],
                    left_on='doc_id', right_on='ROW_ID').drop('ROW_ID', axis=1)

        self.sents = self.sents.apply(self.extract_sent, axis=1)
        self.sents = self.sents.rename({'TEXT': 'text'}, axis=1)

        # Add position of sentence in document to sentences df
        self.sents = self.set_sentence_pos(self.sents)

        # remove sentences without entities
        sents_with_mentions = self.sents[
                    self.sents['sent_id'].isin(
                        self.mentions.drop_duplicates(subset='sent_id')['sent_id']
                    )
                ]

        # Remove umls concepts which don't have a preferred text field
        self.umls = self.umls[~self.umls['preferred_text'].isna()]

        # Prep mentions
        self.mentions = self.transform_mentions(self.mentions)

        # Add original text to mentions
        self.mentions['text'] = self.mentions.apply(self.get_text_from_sentence, args=(self.notes,), axis=1)

        # Add sentence position to mentions
        self.mentions = self.mentions.merge(sents_with_mentions[['sent_id', 'sentence_number']],
                                    on='sent_id')

        # Prep predicates
        self.preds = self.transform_preds(self.preds)
        # Remove predicates not in sentences with mentions
        self.preds = self.preds[
                    self.preds['sent_id'].isin( sents_with_mentions['sent_id'] )
                ]
        self.preds['text'] = self.preds.apply(self.get_text_from_sentence, args=(self.notes,), axis=1)

        # Assign cui codes to mentions (entities)
        self.mentions[['cui', 'umls_xmi_id', 'preferred_text']] = self.mentions. \
                                                     apply(self.get_cui, args=(self.umls,), axis=1, result_type='expand')

        # Set the template tokens we're going to use
        self.mentions['template_token'] = self.mentions['mention_type']
        self.preds['template_token'] = self.preds['frameset']

        preds_toks = self.preds.apply(self.get_template_tokens, axis=1)
        mentions_toks = self.mentions.apply(self.get_template_tokens, axis=1)   

        # Append the two template tokens dataframes and sort 
        template_tokens = preds_toks.append(mentions_toks)
        temp_tokens = template_tokens.groupby(['sent_id']).apply(lambda x: x.sort_values(['begin']))     

        # Create semantic templates
        sem_templates = template_tokens.sort_values('begin').groupby('sent_id')['token'].apply(' '.join)

        sem_df = pd.DataFrame(sem_templates)

        sem_df.reset_index(level=0, inplace=True)

        sem_df = sem_df.rename(columns={'token': 'sem_template'})

        sem_df = sem_df.merge(self.sents[['sent_id', 'sentence_number', 'doc_id', 'begin', 'end']],
                            left_on='sent_id', right_on='sent_id' )

        temp_by_pos = pd.crosstab(sem_df['sem_template'], sem_df['sentence_number']).apply(lambda x: x / x.sum(), axis=0)


        # Store dataframes for clustering later
        sents_with_mentions.to_parquet(f'{self.output}/sentences.parquet')
        self.mentions.to_parquet(f'{self.output}/mentions.parquet')
        self.umls.to_parquet(f'{self.output}/umls.parquet')

        sem_df.to_parquet(f'{self.output}/templates.parquet')

    def get_df_from_pq(self, root, name):
        return pq.read_table(f'{root}/{name}').to_pandas()

    def transform_preds(self, df):
        df['frameset'] = df['frameset'].apply(lambda x: x.split('.')[0])
        return df

    def transform_mentions(self, mentions):
        # Don't want this to fail if these have already been removed
        try:
            mentions = mentions.drop(
                ['conditional', 'history_of', 'generic', 'polarity', 'discovery_technique', 'subject'],
                axis=1)
        except:
            pass
        
        sorted_df = mentions.groupby(['sent_id', 'begin']) \
                            .apply(lambda x: x.sort_values(['begin', 'end']))
        
        # Drop the mentions that are parts of a larger span.  Only keep the containing span that holds multiple
        # mentions
        deduped = sorted_df.drop_duplicates(['sent_id', 'begin'], keep='last')
        deduped = deduped.drop_duplicates(['sent_id', 'end'], keep='first')
        return deduped.reset_index(drop=True)

    def set_template_token(self, df, column):
        df['template_token'] = df[column]
        return df

    def get_template_tokens(self, row):
        return pd.Series({
            'doc_id': row['doc_id'],
            'sent_id': row['sent_id'],
            'token': row['template_token'],
            'begin': row['begin'],
            'end': row['end']
            })    

    def set_sentence_pos(self, df):
        df = df.groupby(["doc_id"]).apply(lambda x: x.sort_values(["begin"])).reset_index(drop=True)
        df['sentence_number'] = df.groupby("doc_id").cumcount()
        return df

    def extract_sent(self, row):
        begin = row['begin']
        end = row['end']
        row['TEXT'] = row['TEXT'][begin:end]
        return row
            
    def get_text_from_sentence(self, row, notes):
        doc = notes[notes['ROW_ID'] == row['doc_id']]
        b = row['begin']
        e = row['end']
        return doc['TEXT'].iloc[0][b:e]        

    def edit_dist(self, row, term2):
        term1 = row.loc['preferred_text']
        return lev_norm(term1, term2)
        
    def get_cui(self, mention, umls_df):
        ont_arr = list(map(int, mention['ontology_arr'].split())) or None
        ment_text = mention['text']
        
        concepts = umls_df[umls_df['xmi_id'].isin(ont_arr)].loc[:, ['cui', 'preferred_text', 'xmi_id']]
        concepts['dist'] = concepts.apply(self.edit_dist, args=(ment_text,), axis=1)
        sorted_df = concepts.sort_values(by='dist', ascending=True).reset_index(drop=True)
        cui = sorted_df['cui'].iloc[0]
        xmi_id = sorted_df['xmi_id'].iloc[0]
        pref_text = sorted_df['preferred_text'].iloc[0]
        return cui, xmi_id, pref_text