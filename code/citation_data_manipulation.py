import re
from sys import stdin
import os
import string
from transformers import pipeline

ner = pipeline("token-classification", model="Jean-Baptiste/roberta-large-ner-english", aggregation_strategy="simple")

def get_global_id(paper_data, paper_id, author, year, title):
  cnt = 0
  alphabet = string.ascii_lowercase
  for paper in paper_data:
    if paper == paper_id:
      data = paper_data[paper]
      if data["Title"] == title:
        return paper
      else:
        cnt += 1
  
  if cnt == 0:
    return paper_id
  
  return f"{paper_id}{alphabet[cnt]}"


def get_title_from_ref(ref):
  entities = ner(ref.strip())
  parts = re.split(r'[,.;]', ref)

  if '\"' in ref:
    title = ref.split('\"')[1]
    return title

  for part in parts:
    find_names = ner(part.strip())
    if any(((element['entity_group'] == 'PER') & (element['word'] in part)) for element in find_names):
      continue
    if len(part.split()) >= 3:
      return part

  return ""

def get_author_with_ner(ref):
  entities = ner(ref.strip())
  for entity in entities:
    if entity['entity_group'] == 'PER':
      author = entity['word']
      if author[0] == '.':
        author = author[1:]

      if '.' in author:
        possible_author = author.split('.')

        for name in possible_author:
          if len(name.strip()) > 1:
            return name.strip(), author.strip()
      elif ' and ' in author:
        return author.split(' and ')[0].strip(), author

      return author.strip(), author.strip()

  if ' and ' in ref:
    if ',' in ref:
      ref_author = ref.split(',')[0]
      author = ref.replace(',', '')
      return ref_author.strip(), author.strip()
    ref_author = ref.split(' and ')[0]
    return ref_author.strip(), ref.strip()
  
  author = re.sub(r'[,()]', '', ref) 

  return author.strip(), author.strip()

def append_reference_data(paper_data, text_id, citation):
  bibl_file = "./texts/" + text_id + "-bibliography.txt"
  with open(bibl_file, 'r') as file:
    text = file.read()

  refs = text.split('\n')
  title = ""
  author = ""
  ref_author = ""
  year = 0

  for ref in refs:
    if len(citation) == 1:
      if ref[0] == citation or citation == ref[1]:
        title = get_title_from_ref(ref)
        year = re.search(r"\d{4}", ref).group()
        ref_author, author = get_author_with_ner(ref)
        break
    elif len(citation) == 2:
      if re.search(r"\d{2}", ref).group() == citation:
        title = get_title_from_ref(ref)
        year = re.search(r"\d{4}", ref).group()
        ref_author, author = get_author_with_ner(ref)
        break
    elif len(citation) >= 3:
      year = re.search(r"\d{4}", citation).group()
      if year in ref:
        ref_author, author = get_author_with_ner(citation.replace(year, ''))
        if ref_author in ref:
          title = get_title_from_ref(ref)
          break

  id_author = re.sub(r'[^A-Za-z ]', '', ref_author).replace(" and ","And").replace(" ", "")
  id = f"{id_author}EtAl{year}"
  if 'And' in id_author:
    id = f"{id_author}{year}"
  title = title.strip()
      

  global_id = get_global_id(paper_data, id, author, year, title)

  paper_data[global_id] = {
    "Author": author,
    "Title": title,
    "Year": year
  }
  return global_id
