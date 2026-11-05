OPTIONS (SKIP=1, ROWS=5000, BINDSIZE=20000000, READSIZE=20000000, ERRORS=0)
LOAD DATA
CHARACTERSET AL32UTF8
INFILE 'csv/19_HEBERGEMENT.csv'
APPEND INTO TABLE HEBERGEMENT
FIELDS TERMINATED BY ';' OPTIONALLY ENCLOSED BY '"' TRAILING NULLCOLS
(
  etablissement_id CHAR(36) "HEXTORAW(REPLACE(:etablissement_id, '-', ''))",
  numeroHebergement CHAR(40),
  typeHebergement CHAR(120),
  capaciteHebergement,
  prixNuitHebergement,
  descriptionHebergement CHAR(2000),
  actifHebergement
)
