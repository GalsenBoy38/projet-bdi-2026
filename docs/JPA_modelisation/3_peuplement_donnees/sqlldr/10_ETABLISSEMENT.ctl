OPTIONS (SKIP=1, ROWS=5000, BINDSIZE=20000000, READSIZE=20000000, ERRORS=0)
LOAD DATA
CHARACTERSET AL32UTF8
INFILE 'csv/10_ETABLISSEMENT.csv'
APPEND INTO TABLE ETABLISSEMENT
FIELDS TERMINATED BY ';' OPTIONALLY ENCLOSED BY '"' TRAILING NULLCOLS
(
  idEtablissement CHAR(36) "HEXTORAW(REPLACE(:idEtablissement, '-', ''))",
  nomCommercial CHAR(400),
  adresse CHAR(320),
  codePostalEtablissement CHAR(20),
  nomCommuneEtablissement CHAR(200),
  codeInsee CHAR(20),
  telephoneEtablissement CHAR(120),
  emailEtablissement CHAR(600),
  siteWebEtablissement CHAR(1400),
  capaciteAccueil,
  classement CHAR(200),
  dateClassement DATE "YYYY-MM-DD",
  classementProroge,
  latitudeEtablissement,
  longitudeEtablissement,
  osmRef CHAR(100),
  noteMoyenne,
  nbNotes,
  idUtilisateur CHAR(36) "HEXTORAW(REPLACE(:idUtilisateur, '-', ''))"
)
