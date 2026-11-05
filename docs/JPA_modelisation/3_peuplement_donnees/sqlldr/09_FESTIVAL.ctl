OPTIONS (SKIP=1, ROWS=5000, BINDSIZE=20000000, READSIZE=20000000, ERRORS=0)
LOAD DATA
CHARACTERSET AL32UTF8
INFILE 'csv/09_FESTIVAL.csv'
APPEND INTO TABLE FESTIVAL
FIELDS TERMINATED BY ';' OPTIONALLY ENCLOSED BY '"' TRAILING NULLCOLS
(
  id CHAR(36) "HEXTORAW(REPLACE(:id, '-', ''))",
  nomFestival CHAR(400),
  domaine CHAR(160),
  sousDomaine CHAR(280),
  periodicite CHAR(120),
  moisDebut,
  siteWebFestival CHAR(600),
  numIdentification CHAR(200),
  dateCreation DATE "YYYY-MM-DD",
  codePostalFestival CHAR(20),
  dateDebutAncien DATE "YYYY-MM-DD",
  dateFinAncien DATE "YYYY-MM-DD",
  dateDebutFestival DATE "YYYY-MM-DD",
  dateFinFestival DATE "YYYY-MM-DD",
  quotaPass,
  nbPassVendus,
  prixPass,
  actifFestival,
  commune_id CHAR(20),
  organisateur_id CHAR(36) "HEXTORAW(REPLACE(:organisateur_id, '-', ''))"
)
