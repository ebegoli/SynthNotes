import pandas as pd



class Generator(object):
    def __init__(self, pq_files, output_dir):
        self.data_dir = pq_files
        self.output_dir = output_dir


    def template_filler(self, template, sentences, entities, all_mentions):
        
        template_id = template.iloc[0]['sent_id']
        
        ments_in_temp = all_mentions[all_mentions.sent_id == template_id]
        
        raw_sentence = sentences[sentences.sent_id == template_id]

        sent_begin = raw_sentence.iloc[0].begin
        sent_end = raw_sentence.iloc[0].end

        raw_text = raw_sentence.iloc[0].text
        
        replacements = []

        for i, row in ments_in_temp.iterrows():
            ents_subset = entities[entities.mention_type == row.mention_type]

            if len(ents_subset) == 0:
                print('Empty list of doc entities')
                print(entities.mention_type)
                print(row.mention_type)
                break
            rand_ent = ents_subset.sample(n=1)
            entities = entities[entities['id'] != rand_ent.iloc[0]['id']]
        
            
            ent_cui = rand_ent.iloc[0].cui

            span_text = self.get_text_for_mention(ent_cui, all_mentions)
            replacements.append({
                'text' : span_text,
                'begin' : row.begin - sent_begin,
                'end' : row.end - sent_begin,
            })
            
        new_sentence = ''
        for i, r in enumerate(replacements):
            if i == 0:
                new_sentence += raw_text[0 : r['begin'] ]
            else:
                new_sentence += raw_text[replacements[i-1]['end'] : r['begin']]
            new_sentence += r['text']
        
        if(len(replacements) > 1):
            new_sentence += raw_text[replacements[-1]['end'] : ]
            
        # clean up
        return new_sentence, entities              

    def get_text_for_mention(self,cui, mentions):
        # Find all the text associated with the cui of the mention in the template
        # choose a text span based on frequency
        txt_counts = mentions[mentions.cui == cui].groupby('text').size().reset_index(name='cnt')
        return txt_counts.sample(n=1, weights=txt_counts.cnt).iloc[0].text

    def generate(self, n_notes=1):
        templates = pd.read_parquet(f'{self.data_dir}/templates.parquet' )
        sentences = pd.read_parquet(f'{self.data_dir}/sentences.parquet')
        mentions = pd.read_parquet(f'{self.data_dir}/mentions.parquet')
        umls = pd.read_parquet(f'{self.data_dir}/umls.parquet')
        cluster_label_by_sentence_pos = pd.read_parquet(f'{self.data_dir}/cluster_by_pos.parquet')                                           

        for i in range(n_notes):
            note = self._generate(templates, sentences, mentions, umls, cluster_label_by_sentence_pos)
            with open(f'{self.output_dir}/note_{i}.txt', 'w') as f:
                f.write(note)

    def _generate(self, templates, sentences, mentions, umls, cluster_label_by_sentence_pos):
        
        doc = sentences['doc_id'].sample(n=1)
        doc_id = doc.iloc[0]
        print(f'Writing note for document {doc_id}')
        ents_in_doc = mentions[mentions['doc_id'] == doc_id]
        
        new_doc_sentences = []
        sent_pos = 0

        def all_ents_present(row, doc_ents, ments_pool):
                # Get mentions in this template
                all_temp_ments = ments_pool[ments_pool['sent_id'] == row['sent_id']]
                available_mentions = all_temp_ments[all_temp_ments['mention_type'].isin(doc_ents['mention_type'])]
                
                return (len(available_mentions) > 0)

        while len(ents_in_doc) > 0:
            # Get list of possible mentions based on CUIs found in the document
            mentions_pool = mentions[(mentions.cui.isin(ents_in_doc.cui.unique()))
                                    & (mentions.mention_type.isin(ents_in_doc.mention_type.unique()))]

            # Get template pool based on mentions pool
            template_candidates = templates[templates.sent_id.isin(mentions_pool.sent_id)]
            
            mask = template_candidates.apply(all_ents_present,
                                            args=(ents_in_doc, mentions_pool),
                                            axis=1)
            template_candidates = template_candidates[mask]
            #If there are no more possible templates then break
            if len(template_candidates) == 0:
                break

            # Get candidate clusters based on template pool
            # Remove the cluster labels that aren't present in template bank
            candidate_cluster_labels = template_candidates.cluster.sort_values().unique()
            candidate_clusters = cluster_label_by_sentence_pos.iloc[candidate_cluster_labels]

            # Select cluster based on frequency at sentence position
            selected_cluster = None
            try:
                selected_cluster = candidate_clusters.sample(
                                                        n=1,
                                                        weights=candidate_clusters.loc[:,sent_pos]
                                        ).iloc[0].name
            except:
                # It's possible the clusters we chose don't appear at that position
                # so we can choose randomly
                selected_cluster = candidate_clusters.sample(n=1).iloc[0].name
            cluster_templates = template_candidates[template_candidates.cluster == selected_cluster]

            # Choose template from cluster at random
            template = cluster_templates.sample(n=1)
            template_id = template.iloc[0]['sent_id']
            
            # Get mentions in the template   
            ments_in_temp = mentions[mentions.sent_id == template_id]

            # Write the sentence and update entities found in the document !!!
            t, ents_in_doc = self.template_filler(template, sentences, ents_in_doc, mentions_pool)
            new_doc_sentences.append(t)
            sent_pos += 1

        return '\n'.join(new_doc_sentences)

