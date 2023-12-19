import os
import torch
import warnings
import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData
from sentence_transformers import SentenceTransformer, util
warnings.filterwarnings('ignore')

class CitySearch:
    def __init__(self):
        load_dotenv()
        db_name = os.getenv("DB_NAME")
        db_password = os.getenv("DB_PASSWORD")
        db_username = os.getenv("DB_USERNAME")
        engine = create_engine(f"postgresql://{db_username}:{db_password}@localhost:5432/{db_name}")
        self.labse = SentenceTransformer('sentence-transformers/LaBSE', device=device)
        self.cities = None
        self.embeddings = None

    def preprocess_data(self):
        self.cities = pd.read_sql_query('''
		WITH region_table AS (
        SELECT
          SUBSTRING(concat_codes FROM '^[A-Z]+\.[A-Z0-9]+') AS country_region,
          asciiname,
          geonameid
        FROM
          admin_codes),
        cities15_filter AS (
        SELECT
          geonameid,
          asciiname,
          alternatenames,
          country_code,
          CONCAT(country_code, '.', admin1_code) AS country_region
        FROM
          geoname_cities15000)
      
        SELECT
          cities15_filter.geonameid,
          cities15_filter.asciiname AS name,
          region_table.asciiname AS region,
          country_code,
          alternatenames
        FROM
          cities15_filter
          LEFT JOIN region_table USING(country_region)
        ''', con=engine)

    def get_embeddings(self):
        self.embeddings = self.labse.encode(self.cities.alternatenames.drop_duplicates().values)

    def similar_search(self, input_city_name, top_matches=5):
        '''
        На вход получает название города и необходимое количество
        схожих наименований к выдаче.
        Возвращает список словарей со схожими наименованиями в формате:
        {введённое название города: [geonameid, name, region, country, cosine_similarity]}.
        '''
        res = util.semantic_search(self.labse
								   .encode(input_city_name), self.embeddings, top_k=top_matches)
        idx = [i['corpus_id'] for i in res[0]]
        score = [i['score'] for i in res[0]]
        result = (self.cities.loc[idx, ['geonameid', 'name', 'region', 'country']]
				  .assign(cosine_similarity=score)
				  .drop_duplicates(subset=['geonameid', 'name'])
				  .iloc[:top_matches])
        return [{input_city_name: [row['geonameid'], 
								   row['name'], 
								   row['region'], 
								   row['country'], 
								   round(row['cosine_similarity'], 2)]}
				for _, row in result.iterrows()]