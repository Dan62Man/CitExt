import re
from sys import stdin
import os
from transformers import pipeline

ner = pipeline("token-classification", model="Jean-Baptiste/roberta-large-ner-english", aggregation_strategy="simple")

def get_title_from_ref(ref):
  entities = ner(ref.strip())
  parts = re.split(r'[,.;]', ref)

  if '\"' in ref:
    title = ref.split('\"')[1]
    print(title)
    return title

  for part in parts:
    find_names = ner(part.strip())
    if any( element['entity_group'] == 'PER' for element in find_names):
      continue
    if len(part.split()) >= 3:
      return part

  return ""

def get_author_with_ner(ref):
  entities = ner(ref.strip())
  for entity in entities:
    if entity['entity_group'] == 'PER':
      author = entity['word']
      return author, author
  
  if ' and ' in ref:
    if ',' in ref:
      ref_author = ref.split(',')[0]
      author = ref.replace(',', '')
      return ref_author, author
    ref_author = ref.split(' and ')[0]
    return ref_author, ref
  
  author = re.sub(r'[,()]', '', ref) 

  return author, author

def append_reference_data(paper_data, text_id, citation):
  bibl_file = "./texts/" + text_id + "-bibliography.txt"
  with open(bibl_file, 'r') as file:
    text = file.read()

  refs = text.split('\n')
  title = ""
  author = ""
  year = 0

  for ref in refs:
    if ref[0] == citation or citation == ref[1]:
      title = get_title_from_ref(ref)
      year = re.search(r"\d{4}", ref).group()
      ref_author, author = get_author_with_ner(ref)
      break
    elif len(citation) >= 3:
      year = re.search(r"\d{4}", citation).group()
      if year in ref:
        ref_author, author = get_author_with_ner(citation.replace(year, ''))
        if author in ref:
          title = get_title_from_ref(ref)
          break

  for paper in paper_data:
    data = paper_data[paper]
    if str(year) == data["Year"] and author.strip() == data["Author"]:
      return paper

  global_id = len(paper_data)

  author = re.sub(r'[^A-Za-z ]', '', author).replace(" and ","").replace(" ", "")
  id = f"{author}EtAl{year}"
  if 'And' in author:
    id = f"{author}{year}"
  title = re.sub(r'^\s', '', title)
  paper_data[global_id] = {
    "ID": id,
    "Author": author,
    "Title": title,
    "Year": year
  }
  return global_id
