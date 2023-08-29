import re
from sys import stdin
import os
from transformers import pipeline

ner = pipeline("token-classification", model="Jean-Baptiste/roberta-large-ner-english", aggregation_strategy="simple")

def get_first_author_from_number(names):
  for name in names:
    if ' and ' in name:
      split_names = name.split(' and ')
      first_last_name = split_names[0].split(' ')[-1]
      second_last_name = re.split(r'[ .]', split_names[1])[-1]
      return f"{first_last_name}And{second_last_name}"
    pattern = re.compile(r'[A-Z]\.')
    matches = pattern.findall(name)
    if matches:
      first_last_name = name.split('.')[-1].strip()
    else:
      first_last_name = name.split(' ')[-1].strip()
    return first_last_name  # Break the loop after finding the first match
  return ""


def get_title_from_number(ref):
  parts = re.split(r'[,.;]', ref)

  if '"' in ref:
    return ref.split('"')[1]

  for part in parts:
    if 'and' in part:
      continue
    elif len(part.split()) >= 3:
      return part

  return ""

def get_year_from_number(ref):
  year_matches = re.findall(r'(?:\.|\,) \d{4}(?:\.|\,)', ref)

  for year_match in year_matches:
    year = year_match.strip('. ,')
    return year
  return 0

def get_author_with_ner(ref):
  entities = ner(ref)
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
  ref_found = False

  for ref in refs:
    if ref[0] == citation or citation == ref[1]:
      title = get_title_from_number(ref)
      year = get_year_from_number(ref)
      ref_author, author = get_author_with_ner(ref)
      #author = get_first_author_from_number(ref.split(','))
      break
    else:
      year = re.search(r"\d{4}", citation).group()
      if year in ref:
        ref_author, author = get_author_with_ner(citation.replace(year, ''))
        #ref_author, author = get_author_from_authors(citation)
        if author in ref:
          title = get_title_from_number(ref)
          break

  for paper in paper_data:
    data = paper_data[paper]
    if str(year) == data["Year"] and author == data["Author"]:
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
