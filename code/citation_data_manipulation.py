import re
from sys import stdin
import os
import string
from transformers import pipeline

ner = pipeline("token-classification", model="Jean-Baptiste/roberta-large-ner-english", aggregation_strategy="simple")

def get_global_id(paper_data, paper_id, author, year, title):
  cnt = 0
  alphabet = string.ascii_lowercase
  while cnt < 25:
    if paper_id in paper_data:
      data = paper_data[paper_id]
      if data["Title"] == title:
        return paper_id
      else:
        cnt += 1
        paper_id = f"{paper_id}{alphabet[cnt]}"
    else:
      return paper_id

  return f"{paper_id}{alphabet[cnt]}"


def get_title_from_ref(ref):
  entities = ner(ref.strip())
  parts = re.split(r'[,.;]', ref)

  if '\"' in ref:
    title = ref.split('\"')[1]
    return title

  for part in parts:
    if len(part.split()) < 3: 
      continue
    
    find_names = ner(part.strip())

    if any(((element['entity_group'] == 'PER') & (element['word'] in part)) for element in find_names):
      continue
    
    if part.startswith("and "):
      continue
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

def get_data_from_numbered_bib(ref, citation):
  title = get_title_from_ref(ref)
  year = re.search(r"\d{4}", ref).group()
  ref_author, author = get_author_with_ner(ref)
  return ref_author, author, year, title


def append_reference_data(paper_data, text_id, citation):
  bibl_file = "./texts/" + text_id + "-bibliography.txt"
  with open(bibl_file, 'r', encoding="utf-8") as file:
    text = file.read()

  refs = text.split('\n')
  title = ""
  author = ""
  ref_author = ""
  year = 0

  for ref in refs:
    if len(citation) == 1:
      if ref[0] == citation or citation == ref[1]:
        ref_author, author, year, title = get_data_from_numbered_bib(ref, citation)
        break

    elif len(citation) == 2:
      if re.search(r"\d{2}", ref).group() == citation:
        ref_author, author, year, title = get_data_from_numbered_bib(ref, citation)
        break

    elif len(citation) >= 3:
      year = re.search(r"\d{4}", citation).group()

      if year in ref:
        ref_author, author = get_author_with_ner(citation.replace(year, ''))

        if ' and ' in ref_author:
          ref_authors = ref_author.split(' and ')

          if ref_authors[0] in ref and ref_authors[1] in ref:
            title = get_title_from_ref(ref)

        elif ref_author in ref:
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
