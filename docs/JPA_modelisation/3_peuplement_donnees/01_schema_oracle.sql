-- FestiBed - Groupe 3 - Schéma Oracle
-- Généré par schema_festibed.py : ne pas modifier à la main.

CREATE TABLE REGION (
  id                               RAW(16) NOT NULL,
  nomRegion                        VARCHAR2(30 CHAR) NOT NULL,
  CONSTRAINT PK_REGION PRIMARY KEY (id),
  CONSTRAINT UK_REGION_1 UNIQUE (nomRegion)
);

CREATE TABLE DEPARTEMENT (
  codeDepartement                  VARCHAR2(3 CHAR) NOT NULL,
  nomDepartement                   VARCHAR2(50 CHAR) NOT NULL,
  region_id                        RAW(16) NOT NULL,
  CONSTRAINT PK_DEPARTEMENT PRIMARY KEY (codeDepartement),
  CONSTRAINT FK_DEPARTEMENT_1 FOREIGN KEY (region_id) REFERENCES REGION (id)
);

CREATE TABLE COMMUNE (
  codeInsee                        VARCHAR2(5 CHAR) NOT NULL,
  nomCommune                       VARCHAR2(40 CHAR) NOT NULL,
  latitude                         NUMBER(12,9),
  longitude                        NUMBER(12,9),
  departement_id                   VARCHAR2(3 CHAR) NOT NULL,
  CONSTRAINT PK_COMMUNE PRIMARY KEY (codeInsee),
  CONSTRAINT FK_COMMUNE_1 FOREIGN KEY (departement_id) REFERENCES DEPARTEMENT (codeDepartement),
  CONSTRAINT CK_COMMUNE_1 CHECK (latitude BETWEEN -90 AND 90),
  CONSTRAINT CK_COMMUNE_2 CHECK (longitude BETWEEN -180 AND 180)
);

CREATE TABLE UTILISATEUR (
  id                               RAW(16) NOT NULL,
  nom                              VARCHAR2(100 CHAR) NOT NULL,
  email                            VARCHAR2(150 CHAR) NOT NULL,
  CONSTRAINT PK_UTILISATEUR PRIMARY KEY (id),
  CONSTRAINT UK_UTILISATEUR_1 UNIQUE (email)
);

CREATE TABLE FESTIVALIER (
  id                               RAW(16) NOT NULL,
  fournisseurAuth                  VARCHAR2(30 CHAR),
  identifiantExterneFestivalier    VARCHAR2(100 CHAR),
  CONSTRAINT PK_FESTIVALIER PRIMARY KEY (id),
  CONSTRAINT UK_FESTIVALIER_1 UNIQUE (fournisseurAuth, identifiantExterneFestivalier),
  CONSTRAINT FK_FESTIVALIER_1 FOREIGN KEY (id) REFERENCES UTILISATEUR (id)
);

CREATE TABLE UTILISATEUR_BACKOFFICE (
  id                               RAW(16) NOT NULL,
  motDePasseHache                  VARCHAR2(100 CHAR) NOT NULL,
  CONSTRAINT PK_UTILISATEUR_BACKOFFICE PRIMARY KEY (id),
  CONSTRAINT FK_UTILISATEUR_BACKOFFICE_1 FOREIGN KEY (id) REFERENCES UTILISATEUR (id)
);

CREATE TABLE ORGANISATEUR (
  id                               RAW(16) NOT NULL,
  CONSTRAINT PK_ORGANISATEUR PRIMARY KEY (id),
  CONSTRAINT FK_ORGANISATEUR_1 FOREIGN KEY (id) REFERENCES UTILISATEUR_BACKOFFICE (id)
);

CREATE TABLE HEBERGEUR (
  id                               RAW(16) NOT NULL,
  CONSTRAINT PK_HEBERGEUR PRIMARY KEY (id),
  CONSTRAINT FK_HEBERGEUR_1 FOREIGN KEY (id) REFERENCES UTILISATEUR_BACKOFFICE (id)
);

CREATE TABLE FESTIVAL (
  id                               RAW(16) NOT NULL,
  nomFestival                      VARCHAR2(100 CHAR) NOT NULL,
  domaine                          VARCHAR2(40 CHAR) NOT NULL,
  sousDomaine                      VARCHAR2(70 CHAR),
  periodicite                      VARCHAR2(30 CHAR),
  moisDebut                        NUMBER(2) NOT NULL,
  siteWebFestival                  VARCHAR2(150 CHAR),
  numIdentification                VARCHAR2(50 CHAR),
  dateCreation                     DATE,
  codePostalFestival               VARCHAR2(5 CHAR) NOT NULL,
  dateDebutAncien                  DATE,
  dateFinAncien                    DATE,
  dateDebutFestival                DATE NOT NULL,
  dateFinFestival                  DATE NOT NULL,
  quotaPass                        NUMBER(10) NOT NULL,
  nbPassVendus                     NUMBER(10) DEFAULT 0 NOT NULL,
  prixPass                         NUMBER(8,2) NOT NULL,
  actifFestival                    NUMBER(1) DEFAULT 1 NOT NULL,
  commune_id                       VARCHAR2(5 CHAR) NOT NULL,
  organisateur_id                  RAW(16),
  CONSTRAINT PK_FESTIVAL PRIMARY KEY (id),
  CONSTRAINT FK_FESTIVAL_1 FOREIGN KEY (commune_id) REFERENCES COMMUNE (codeInsee),
  CONSTRAINT FK_FESTIVAL_2 FOREIGN KEY (organisateur_id) REFERENCES ORGANISATEUR (id),
  CONSTRAINT CK_FESTIVAL_1 CHECK (moisDebut BETWEEN 1 AND 12),
  CONSTRAINT CK_FESTIVAL_2 CHECK (dateFinFestival >= dateDebutFestival),
  CONSTRAINT CK_FESTIVAL_3 CHECK (quotaPass >= 0),
  CONSTRAINT CK_FESTIVAL_4 CHECK (nbPassVendus BETWEEN 0 AND quotaPass),
  CONSTRAINT CK_FESTIVAL_5 CHECK (prixPass >= 0),
  CONSTRAINT CK_FESTIVAL_6 CHECK (domaine IN ('MUSIQUES_ACTUELLES', 'CINEMA_ET_AUDIOVISUEL', 'MUSIQUES_CLASSIQUES', 'CIRQUE_ET_ARTS_DE_LA_RUE', 'LIVRE_ET_LITTERATURE', 'DANSE', 'THEATRE', 'ARTS_PLASTIQUES_ET_VISUELS', 'PLURIDISCIPLINAIRE_SPECTACLE_VIVANT', 'PLURIDISCIPLINAIRE_MUSIQUE', 'DIVERS_SPECTACLE_VIVANT', 'TRANSDISCIPLINAIRE', 'DOMAINES_DIVERS')),
  CONSTRAINT CK_FESTIVAL_7 CHECK (sousDomaine IN ('AMPLIFIEES_OU_ELECTRONIQUES', 'JAZZ_BLUES_ET_IMPROVISEES', 'CHANSON', 'TRADITIONNELLES_ET_DU_MONDE', 'BAROQUE_ET_ANCIEN', 'ARTS_DE_LA_RUE')),
  CONSTRAINT CK_FESTIVAL_8 CHECK (periodicite IN ('ANNUELLE', 'BIENNALE_ANNEES_PAIRES', 'BIENNALE_ANNEES_IMPAIRES', 'BIANNUELLE', 'IRREGULIERE')),
  CONSTRAINT CK_FESTIVAL_9 CHECK (actifFestival IN (0, 1))
);

CREATE TABLE ETABLISSEMENT (
  id                               RAW(16) NOT NULL,
  nomCommercial                    VARCHAR2(100 CHAR) NOT NULL,
  adresse                          VARCHAR2(80 CHAR),
  codePostalEtablissement          VARCHAR2(5 CHAR) NOT NULL,
  nomCommuneEtablissement          VARCHAR2(50 CHAR) NOT NULL,
  commune_id                       VARCHAR2(5 CHAR),
  telephoneEtablissement           VARCHAR2(30 CHAR),
  emailEtablissement               VARCHAR2(150 CHAR),
  siteWebEtablissement             VARCHAR2(350 CHAR),
  capaciteAccueil                  NUMBER(10) NOT NULL,
  classement                       VARCHAR2(50 CHAR),
  dateClassement                   DATE,
  classementProroge                NUMBER(1),
  latitudeEtablissement            NUMBER(12,9),
  longitudeEtablissement           NUMBER(12,9),
  osmRef                           VARCHAR2(25 CHAR),
  noteMoyenne                      NUMBER(3,2),
  nbNotes                          NUMBER(10) DEFAULT 0 NOT NULL,
  hebergeur_id                     RAW(16),
  CONSTRAINT PK_ETABLISSEMENT PRIMARY KEY (id),
  CONSTRAINT UK_ETABLISSEMENT_1 UNIQUE (osmRef),
  CONSTRAINT FK_ETABLISSEMENT_1 FOREIGN KEY (commune_id) REFERENCES COMMUNE (codeInsee),
  CONSTRAINT FK_ETABLISSEMENT_2 FOREIGN KEY (hebergeur_id) REFERENCES HEBERGEUR (id),
  CONSTRAINT CK_ETABLISSEMENT_1 CHECK (capaciteAccueil > 0),
  CONSTRAINT CK_ETABLISSEMENT_2 CHECK (noteMoyenne BETWEEN 1 AND 5),
  CONSTRAINT CK_ETABLISSEMENT_3 CHECK (nbNotes >= 0),
  CONSTRAINT CK_ETABLISSEMENT_4 CHECK ((classement IS NULL AND dateClassement IS NULL AND classementProroge IS NULL) OR (classement IS NOT NULL AND dateClassement IS NOT NULL AND classementProroge IS NOT NULL)),
  CONSTRAINT CK_ETABLISSEMENT_5 CHECK (classement IN ('UNE_ETOILE', 'DEUX_ETOILES', 'TROIS_ETOILES', 'QUATRE_ETOILES', 'CINQ_ETOILES', 'AUBERGE_COLLECTIVE', 'AIRE_NATURELLE')),
  CONSTRAINT CK_ETABLISSEMENT_6 CHECK (classementProroge IN (0, 1))
);

CREATE TABLE HOTEL_DE_TOURISME (
  id                               RAW(16) NOT NULL,
  nbChambresHotel                  NUMBER(10) NOT NULL,
  CONSTRAINT PK_HOTEL_DE_TOURISME PRIMARY KEY (id),
  CONSTRAINT FK_HOTEL_DE_TOURISME_1 FOREIGN KEY (id) REFERENCES ETABLISSEMENT (id)
);

CREATE TABLE AUBERGE_COLLECTIVE (
  id                               RAW(16) NOT NULL,
  nbChambresAuberge                NUMBER(10) NOT NULL,
  CONSTRAINT PK_AUBERGE_COLLECTIVE PRIMARY KEY (id),
  CONSTRAINT FK_AUBERGE_COLLECTIVE_1 FOREIGN KEY (id) REFERENCES ETABLISSEMENT (id)
);

CREATE TABLE CAMPING (
  id                               RAW(16) NOT NULL,
  categorie                        VARCHAR2(10 CHAR),
  nbEmplacementsCamping            NUMBER(10) NOT NULL,
  CONSTRAINT PK_CAMPING PRIMARY KEY (id),
  CONSTRAINT FK_CAMPING_1 FOREIGN KEY (id) REFERENCES ETABLISSEMENT (id),
  CONSTRAINT CK_CAMPING_1 CHECK (categorie IN ('TOURISME', 'LOISIRS'))
);

CREATE TABLE PARC_RESIDENTIEL_DE_LOISIRS (
  id                               RAW(16) NOT NULL,
  nbEmplacementsParc               NUMBER(10) NOT NULL,
  CONSTRAINT PK_PARC_RESIDENTIEL_DE_LOISIRS PRIMARY KEY (id),
  CONSTRAINT FK_PARC_RESIDENTIEL_DE_LOISI_1 FOREIGN KEY (id) REFERENCES ETABLISSEMENT (id)
);

CREATE TABLE VILLAGE_DE_VACANCES (
  id                               RAW(16) NOT NULL,
  mention                          VARCHAR2(30 CHAR),
  typeSejour                       VARCHAR2(30 CHAR),
  nbLogements                      NUMBER(10) NOT NULL,
  CONSTRAINT PK_VILLAGE_DE_VACANCES PRIMARY KEY (id),
  CONSTRAINT FK_VILLAGE_DE_VACANCES_1 FOREIGN KEY (id) REFERENCES ETABLISSEMENT (id),
  CONSTRAINT CK_VILLAGE_DE_VACANCES_1 CHECK (mention IN ('NON', 'HEBERGEMENT_DISPERSE', 'HEBERGEMENT_LEGER', 'HEBERGEMENT_LEGER_ET_DISPERSE')),
  CONSTRAINT CK_VILLAGE_DE_VACANCES_2 CHECK (typeSejour IN ('FORMULE_PENSION', 'FORMULE_LOCATION', 'FORMULE_LOCATION_PENSION'))
);

CREATE TABLE RESIDENCE_DE_TOURISME (
  id                               RAW(16) NOT NULL,
  nbUnitesHabitation               NUMBER(10) NOT NULL,
  CONSTRAINT PK_RESIDENCE_DE_TOURISME PRIMARY KEY (id),
  CONSTRAINT FK_RESIDENCE_DE_TOURISME_1 FOREIGN KEY (id) REFERENCES ETABLISSEMENT (id)
);

CREATE TABLE ETABLISSEMENT_NON_CLASSE (
  id                               RAW(16) NOT NULL,
  typeNonClasse                    VARCHAR2(30 CHAR) NOT NULL,
  nbEtoilesDeclarees               NUMBER(1),
  nbChambres                       NUMBER(10),
  nbLits                           NUMBER(10),
  CONSTRAINT PK_ETABLISSEMENT_NON_CLASSE PRIMARY KEY (id),
  CONSTRAINT FK_ETABLISSEMENT_NON_CLASSE_1 FOREIGN KEY (id) REFERENCES ETABLISSEMENT (id),
  CONSTRAINT CK_ETABLISSEMENT_NON_CLASSE_1 CHECK (nbEtoilesDeclarees BETWEEN 1 AND 5),
  CONSTRAINT CK_ETABLISSEMENT_NON_CLASSE_2 CHECK (nbChambres > 0),
  CONSTRAINT CK_ETABLISSEMENT_NON_CLASSE_3 CHECK (nbLits > 0),
  CONSTRAINT CK_ETABLISSEMENT_NON_CLASSE_4 CHECK (typeNonClasse IN ('HOTEL', 'MOTEL', 'CHAMBRE_D_HOTES', 'GITE_CHALET', 'APPARTEMENT', 'AUBERGE_DE_JEUNESSE', 'CAMPING', 'AIRE_DE_CAMPING_CAR', 'REFUGE_GARDE'))
);

CREATE TABLE OPTION_HEBERGEMENT (
  id                               RAW(16) NOT NULL,
  libelleOptionHebergement         VARCHAR2(50 CHAR) NOT NULL,
  CONSTRAINT PK_OPTION_HEBERGEMENT PRIMARY KEY (id),
  CONSTRAINT UK_OPTION_HEBERGEMENT_1 UNIQUE (libelleOptionHebergement)
);

CREATE TABLE HEBERGEMENT (
  etablissement_id                 RAW(16) NOT NULL,
  numeroHebergement                VARCHAR2(10 CHAR) NOT NULL,
  typeHebergement                  VARCHAR2(30 CHAR) NOT NULL,
  capaciteHebergement              NUMBER(10) NOT NULL,
  prixNuitHebergement              NUMBER(8,2) NOT NULL,
  descriptionHebergement           VARCHAR2(500 CHAR),
  actifHebergement                 NUMBER(1) DEFAULT 1 NOT NULL,
  CONSTRAINT PK_HEBERGEMENT PRIMARY KEY (etablissement_id, numeroHebergement),
  CONSTRAINT FK_HEBERGEMENT_1 FOREIGN KEY (etablissement_id) REFERENCES ETABLISSEMENT (id),
  CONSTRAINT CK_HEBERGEMENT_1 CHECK (capaciteHebergement > 0),
  CONSTRAINT CK_HEBERGEMENT_2 CHECK (prixNuitHebergement >= 0),
  CONSTRAINT CK_HEBERGEMENT_3 CHECK (typeHebergement IN ('CHAMBRE_SIMPLE', 'CHAMBRE_DOUBLE', 'EMPLACEMENT_DE_CAMPING', 'BUNGALOW', 'LOGEMENT_ENTIER', 'LIT_EN_DORTOIR')),
  CONSTRAINT CK_HEBERGEMENT_4 CHECK (actifHebergement IN (0, 1))
);

CREATE TABLE PHOTO_HEBERGEMENT (
  id                               RAW(16) NOT NULL,
  urlPhotoHebergement              VARCHAR2(300 CHAR) NOT NULL,
  etablissement_id                 RAW(16) NOT NULL,
  numeroHebergement                VARCHAR2(10 CHAR) NOT NULL,
  CONSTRAINT PK_PHOTO_HEBERGEMENT PRIMARY KEY (id),
  CONSTRAINT FK_PHOTO_HEBERGEMENT_1 FOREIGN KEY (etablissement_id, numeroHebergement) REFERENCES HEBERGEMENT (etablissement_id, numeroHebergement)
);

CREATE TABLE EQUIPEMENT (
  etablissement_id                 RAW(16) NOT NULL,
  numeroHebergement                VARCHAR2(10 CHAR) NOT NULL,
  option_id                        RAW(16) NOT NULL,
  CONSTRAINT PK_EQUIPEMENT PRIMARY KEY (etablissement_id, numeroHebergement, option_id),
  CONSTRAINT FK_EQUIPEMENT_1 FOREIGN KEY (etablissement_id, numeroHebergement) REFERENCES HEBERGEMENT (etablissement_id, numeroHebergement),
  CONSTRAINT FK_EQUIPEMENT_2 FOREIGN KEY (option_id) REFERENCES OPTION_HEBERGEMENT (id)
);

CREATE TABLE RESERVATION (
  numeroReservation                VARCHAR2(20 CHAR) NOT NULL,
  dateReservation                  TIMESTAMP NOT NULL,
  festivalier_id                   RAW(16) NOT NULL,
  CONSTRAINT PK_RESERVATION PRIMARY KEY (numeroReservation),
  CONSTRAINT FK_RESERVATION_1 FOREIGN KEY (festivalier_id) REFERENCES FESTIVALIER (id)
);

CREATE TABLE PAIEMENT (
  id                               RAW(16) NOT NULL,
  numTransaction                   VARCHAR2(30 CHAR),
  montantPaiement                  NUMBER(10,2) NOT NULL,
  datePaiement                     TIMESTAMP,
  statutPaiement                   VARCHAR2(20 CHAR) NOT NULL,
  reservation_id                   VARCHAR2(20 CHAR) NOT NULL,
  CONSTRAINT PK_PAIEMENT PRIMARY KEY (id),
  CONSTRAINT UK_PAIEMENT_1 UNIQUE (numTransaction),
  CONSTRAINT UK_PAIEMENT_2 UNIQUE (reservation_id),
  CONSTRAINT FK_PAIEMENT_1 FOREIGN KEY (reservation_id) REFERENCES RESERVATION (numeroReservation),
  CONSTRAINT CK_PAIEMENT_1 CHECK (montantPaiement >= 0),
  CONSTRAINT CK_PAIEMENT_2 CHECK (statutPaiement IN ('NON_GERE', 'EN_ATTENTE', 'ACCEPTE', 'REFUSE', 'REMBOURSE'))
);

CREATE TABLE SELECTION (
  id                               RAW(16) NOT NULL,
  prixPassSelection                NUMBER(8,2) NOT NULL,
  statutSelection                  VARCHAR2(20 CHAR) NOT NULL,
  reservation_id                   VARCHAR2(20 CHAR) NOT NULL,
  festival_id                      RAW(16) NOT NULL,
  CONSTRAINT PK_SELECTION PRIMARY KEY (id),
  CONSTRAINT UK_SELECTION_1 UNIQUE (reservation_id, festival_id),
  CONSTRAINT FK_SELECTION_1 FOREIGN KEY (reservation_id) REFERENCES RESERVATION (numeroReservation),
  CONSTRAINT FK_SELECTION_2 FOREIGN KEY (festival_id) REFERENCES FESTIVAL (id),
  CONSTRAINT CK_SELECTION_1 CHECK (prixPassSelection >= 0),
  CONSTRAINT CK_SELECTION_2 CHECK (statutSelection IN ('CONFIRMEE', 'ANNULEE'))
);

CREATE TABLE PASS (
  id                               RAW(16) NOT NULL,
  codePass                         VARCHAR2(40 CHAR) NOT NULL,
  selection_id                     RAW(16) NOT NULL,
  CONSTRAINT PK_PASS PRIMARY KEY (id),
  CONSTRAINT UK_PASS_1 UNIQUE (codePass),
  CONSTRAINT FK_PASS_1 FOREIGN KEY (selection_id) REFERENCES SELECTION (id)
);

CREATE TABLE NUITEE (
  etablissement_id                 RAW(16) NOT NULL,
  numeroHebergement                VARCHAR2(10 CHAR) NOT NULL,
  dateNuitee                       DATE NOT NULL,
  prixNuitee                       NUMBER(8,2) NOT NULL,
  selection_id                     RAW(16),
  CONSTRAINT PK_NUITEE PRIMARY KEY (etablissement_id, numeroHebergement, dateNuitee),
  CONSTRAINT FK_NUITEE_1 FOREIGN KEY (etablissement_id, numeroHebergement) REFERENCES HEBERGEMENT (etablissement_id, numeroHebergement),
  CONSTRAINT FK_NUITEE_2 FOREIGN KEY (selection_id) REFERENCES SELECTION (id),
  CONSTRAINT CK_NUITEE_1 CHECK (prixNuitee >= 0)
);

CREATE TABLE NOTATION_FESTIVAL (
  festival_id                      RAW(16) NOT NULL,
  festivalier_id                   RAW(16) NOT NULL,
  noteFestival                     NUMBER(1) NOT NULL,
  dateNoteFestival                 DATE NOT NULL,
  CONSTRAINT PK_NOTATION_FESTIVAL PRIMARY KEY (festival_id, festivalier_id),
  CONSTRAINT FK_NOTATION_FESTIVAL_1 FOREIGN KEY (festival_id) REFERENCES FESTIVAL (id),
  CONSTRAINT FK_NOTATION_FESTIVAL_2 FOREIGN KEY (festivalier_id) REFERENCES FESTIVALIER (id),
  CONSTRAINT CK_NOTATION_FESTIVAL_1 CHECK (noteFestival BETWEEN 1 AND 5)
);

CREATE TABLE NOTATION_ETABLISSEMENT (
  etablissement_id                 RAW(16) NOT NULL,
  festivalier_id                   RAW(16) NOT NULL,
  noteEtablissement                NUMBER(1) NOT NULL,
  dateNoteEtablissement            DATE NOT NULL,
  CONSTRAINT PK_NOTATION_ETABLISSEMENT PRIMARY KEY (etablissement_id, festivalier_id),
  CONSTRAINT FK_NOTATION_ETABLISSEMENT_1 FOREIGN KEY (etablissement_id) REFERENCES ETABLISSEMENT (id),
  CONSTRAINT FK_NOTATION_ETABLISSEMENT_2 FOREIGN KEY (festivalier_id) REFERENCES FESTIVALIER (id),
  CONSTRAINT CK_NOTATION_ETABLISSEMENT_1 CHECK (noteEtablissement BETWEEN 1 AND 5)
);

-- Index : Oracle n'indexe pas automatiquement les clés étrangères.
CREATE INDEX IX_DEPARTEMENT_1 ON DEPARTEMENT (region_id);
CREATE INDEX IX_COMMUNE_1 ON COMMUNE (departement_id);
CREATE INDEX IX_FESTIVAL_1 ON FESTIVAL (dateDebutFestival, dateFinFestival);
CREATE INDEX IX_FESTIVAL_2 ON FESTIVAL (commune_id);
CREATE INDEX IX_FESTIVAL_3 ON FESTIVAL (domaine);
CREATE INDEX IX_FESTIVAL_4 ON FESTIVAL (organisateur_id);
CREATE INDEX IX_ETABLISSEMENT_1 ON ETABLISSEMENT (latitudeEtablissement, longitudeEtablissement);
CREATE INDEX IX_ETABLISSEMENT_2 ON ETABLISSEMENT (codePostalEtablissement);
CREATE INDEX IX_ETABLISSEMENT_3 ON ETABLISSEMENT (hebergeur_id);
CREATE INDEX IX_ETABLISSEMENT_4 ON ETABLISSEMENT (commune_id);
CREATE INDEX IX_ETABLISSEMENT_NON_CLASSE_1 ON ETABLISSEMENT_NON_CLASSE (typeNonClasse);
CREATE INDEX IX_PHOTO_HEBERGEMENT_1 ON PHOTO_HEBERGEMENT (etablissement_id, numeroHebergement);
CREATE INDEX IX_EQUIPEMENT_1 ON EQUIPEMENT (option_id);
CREATE INDEX IX_RESERVATION_1 ON RESERVATION (festivalier_id);
CREATE INDEX IX_SELECTION_1 ON SELECTION (festival_id);
CREATE INDEX IX_PASS_1 ON PASS (selection_id);
CREATE INDEX IX_NUITEE_1 ON NUITEE (dateNuitee, selection_id);
CREATE INDEX IX_NUITEE_2 ON NUITEE (selection_id);
CREATE INDEX IX_NOTATION_FESTIVAL_1 ON NOTATION_FESTIVAL (festivalier_id);
CREATE INDEX IX_NOTATION_ETABLISSEMENT_1 ON NOTATION_ETABLISSEMENT (festivalier_id);
