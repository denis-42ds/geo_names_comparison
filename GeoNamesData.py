import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()
db_password = os.getenv("DB_PASSWORD")
db_username = os.getenv("DB_USERNAME")
db_name = os.getenv("DB_NAME")

engine = create_engine(f"postgresql://{db_username}:{db_password}@localhost:5432/{db_name}")

geoname_columns = ['geonameid', 
				   'name', 
				   'asciiname', 
				   'alternatenames',
				   'latitude', 
				   'longitude', 
				   'feature_class', 
				   'feature_code', 
				   'country_code', 
				   'cc2', 
				   'admin1_code', 
				   'admin2_code', 
				   'admin3_code', 
				   'admin4_code', 
				   'population', 
				   'elevation',
				   'dem', 
				   'timezone', 
				   'modification_date']

def geoname_adding_to_db(file_path: str) -> str:
    '''
    Чтение файла и отправка данных в базу данных.
    Параметры:
    file_path (str): Путь к файлу.
    Возвращает:
    table_name (str): Наименование таблицы в базе данных.
    '''
    # Создание имени таблицы
    table_name = 'geoname_' + (file_path.split('/')[-1].split('.')[0]).lower()

    # Чтение файла в датафрейм
    df = pd.read_csv(file_path, names=geoname_columns, index_col=False, delimiter='\t')

    # Отправка данных в базу данных
    df.to_sql(name=table_name, con=engine, if_exists='append')

    return table_name


'''
The main 'geoname' table has the following fields :
---------------------------------------------------
geonameid         : integer id of record in geonames database
name              : name of geographical point (utf8) varchar(200)
asciiname         : name of geographical point in plain ascii characters, varchar(200)
alternatenames    : alternatenames, comma separated, ascii names automatically transliterated, convenience attribute from alternatename table, varchar(10000)
latitude          : latitude in decimal degrees (wgs84)
longitude         : longitude in decimal degrees (wgs84)
feature class     : see http://www.geonames.org/export/codes.html, char(1)
feature code      : see http://www.geonames.org/export/codes.html, varchar(10)
country code      : ISO-3166 2-letter country code, 2 characters
cc2               : alternate country codes, comma separated, ISO-3166 2-letter country code, 200 characters
admin1 code       : fipscode (subject to change to iso code), see exceptions below, see file admin1Codes.txt for display names of this code; varchar(20)
admin2 code       : code for the second administrative division, a county in the US, see file admin2Codes.txt; varchar(80) 
admin3 code       : code for third level administrative division, varchar(20)
admin4 code       : code for fourth level administrative division, varchar(20)
population        : bigint (8 byte int) 
elevation         : in meters, integer
dem               : digital elevation model, srtm3 or gtopo30, average elevation of 3''x3'' (ca 90mx90m) or 30''x30'' (ca 900mx900m) area in meters, integer. srtm processed by cgiar/ciat.
timezone          : the iana timezone id (see file timeZone.txt) varchar(40)
modification date : date of last modification in yyyy-MM-dd format


AdminCodes:
Most adm1 are FIPS codes. ISO codes are used for US, CH, BE and ME. UK and Greece are using an additional level between country and fips code. The code '00' stands for general features where no specific adm1 code is defined.
The corresponding admin feature is found with the same countrycode and adminX codes and the respective feature code ADMx.
'''
admin_codes_columns = ['concat_codes',
					  'name',
					  'asciiname',
					  'geonameid']

def admincodes_adding_to_db(file_path: str) -> str:
    '''
    Чтение файла и отправка данных в базу данных.
    Параметры:
    file_path (str): Путь к файлу.
    Возвращает:
    table_name (str): Наименование таблицы в базе данных.
    '''
    # Создание имени таблицы
    table_name = 'admin_codes'

    # Чтение файла в датафрейм
    df = pd.read_csv(file_path, names=admin_codes_columns, index_col=False, delimiter='\t')

    # Отправка данных в базу данных
    df.to_sql(name=table_name, con=engine, if_exists='append')

    return table_name
'''
admintocodes file: names for administrative subdivision 'admin2 code' (UTF8), 
Format : concatenated codes <tab>name <tab> asciiname <tab> geonameId
'''

# class AlternateNames(Base):
#     __tablename__ = 'alternate_names'
#     alternateNameId = Column(Integer, primary_key=True)
#     geonameid = Column(Integer)
#     isolanguage = Column(String(7))
#     alternatename = Column(String(400))


'''
The table 'alternate names' :
-----------------------------
alternateNameId   : the id of this alternate name, int
geonameid         : geonameId referring to id in table 'geoname', int
isolanguage       : iso 639 language code 2- or 3-characters, optionally followed by a hyphen and a countrycode for country specific variants (ex:zh-CN) or by a variant name (ex: zh-Hant); 4-characters 'post' for postal codes and 'iata','icao' and faac for airport codes, fr_1793 for French Revolution names,  abbr for abbreviation, link to a website (mostly to wikipedia), wkdt for the wikidataid, varchar(7)
alternate name    : alternate name or name variant, varchar(400)
isPreferredName   : '1', if this alternate name is an official/preferred name
isShortName       : '1', if this is a short name like 'California' for 'State of California'
isColloquial      : '1', if this alternate name is a colloquial or slang term. Example: 'Big Apple' for 'New York'.
isHistoric        : '1', if this alternate name is historic and was used in the past. Example 'Bombay' for 'Mumbai'.
from		  : from period when the name was used
to		  : to period when the name was used

Remark : the field 'alternatenames' in the table 'geoname' is a short version of the 'alternatenames' table without links and postal codes but with ascii transliterations. You probably don't need both. 
If you don't need to know the language of a name variant, the field 'alternatenames' will be sufficient. If you need to know the language
of a name variant, then you will need to load the table 'alternatenames' and you can drop the column in the geoname table.
'''