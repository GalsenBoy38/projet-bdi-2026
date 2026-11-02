-- FestiBed - Groupe 3 - Schéma H2 (tests)
-- Généré par schema_festibed.py : ne pas modifier à la main.

CREATE SEQUENCE SEQ_REGION START WITH 1 INCREMENT BY 50;
CREATE SEQUENCE SEQ_UTILISATEUR START WITH 1 INCREMENT BY 50;
CREATE SEQUENCE SEQ_FESTIVAL START WITH 1 INCREMENT BY 50;
CREATE SEQUENCE SEQ_ETABLISSEMENT START WITH 1 INCREMENT BY 50;
CREATE SEQUENCE SEQ_OPTION_HEBERGEMENT START WITH 1 INCREMENT BY 50;
CREATE SEQUENCE SEQ_PHOTO_HEBERGEMENT START WITH 1 INCREMENT BY 50;
CREATE SEQUENCE SEQ_PAIEMENT START WITH 1 INCREMENT BY 50;
CREATE SEQUENCE SEQ_SELECTION START WITH 1 INCREMENT BY 50;
CREATE SEQUENCE SEQ_PASS START WITH 1 INCREMENT BY 50;

CREATE TABLE REGION (
  idRegion                         BIGINT NOT NULL,
  nomRegion                        VARCHAR(30) NOT NULL,
  CONSTRAINT PK_REGION PRIMARY KEY (idRegion),
  CONSTRAINT UK_REGION_1 UNIQUE (nomRegion)
);

CREATE TABLE DEPARTEMENT (
  codeDepartement                  VARCHAR(3) NOT NULL,
  nomDepartement                   VARCHAR(50) NOT NULL,
  idRegion                         BIGINT NOT NULL,
  CONSTRAINT PK_DEPARTEMENT PRIMARY KEY (codeDepartement),
  CONSTRAINT FK_DEPARTEMENT_1 FOREIGN KEY (idRegion) REFERENCES REGION (idRegion)
);

CREATE TABLE COMMUNE (
  codeInsee                        VARCHAR(5) NOT NULL,
  nomCommune                       VARCHAR(40) NOT NULL,
  latitude                         NUMERIC(12,9),
  longitude                        NUMERIC(12,9),
  codeDepartement                  VARCHAR(3) NOT NULL,
  CONSTRAINT PK_COMMUNE PRIMARY KEY (codeInsee),
  CONSTRAINT FK_COMMUNE_1 FOREIGN KEY (codeDepartement) REFERENCES DEPARTEMENT (codeDepartement),
  CONSTRAINT CK_COMMUNE_1 CHECK (latitude BETWEEN -90 AND 90),
  CONSTRAINT CK_COMMUNE_2 CHECK (longitude BETWEEN -180 AND 180)
);

CREATE TABLE UTILISATEUR (
  idUtilisateur                    BIGINT NOT NULL,
  nom                              VARCHAR(100) NOT NULL,
  email                            VARCHAR(150) NOT NULL,
  CONSTRAINT PK_UTILISATEUR PRIMARY KEY (idUtilisateur),
  CONSTRAINT UK_UTILISATEUR_1 UNIQUE (email)
);

CREATE TABLE FESTIVALIER (
  idUtilisateur                    BIGINT NOT NULL,
  fournisseurAuth                  VARCHAR(30),
  identifiantExterneFestivalier    VARCHAR(100),
  CONSTRAINT PK_FESTIVALIER PRIMARY KEY (idUtilisateur),
  CONSTRAINT UK_FESTIVALIER_1 UNIQUE (fournisseurAuth, identifiantExterneFestivalier),
  CONSTRAINT FK_FESTIVALIER_1 FOREIGN KEY (idUtilisateur) REFERENCES UTILISATEUR (idUtilisateur)
);

CREATE TABLE UTILISATEUR_BACKOFFICE (
  idUtilisateur                    BIGINT NOT NULL,
  motDePasseHache                  VARCHAR(100) NOT NULL,
  CONSTRAINT PK_UTILISATEUR_BACKOFFICE PRIMARY KEY (idUtilisateur),
  CONSTRAINT FK_UTILISATEUR_BACKOFFICE_1 FOREIGN KEY (idUtilisateur) REFERENCES UTILISATEUR (idUtilisateur)
);

CREATE TABLE ORGANISATEUR (
  idUtilisateur                    BIGINT NOT NULL,
  CONSTRAINT PK_ORGANISATEUR PRIMARY KEY (idUtilisateur),
  CONSTRAINT FK_ORGANISATEUR_1 FOREIGN KEY (idUtilisateur) REFERENCES UTILISATEUR_BACKOFFICE (idUtilisateur)
);

CREATE TABLE HEBERGEUR (
  idUtilisateur                    BIGINT NOT NULL,
  CONSTRAINT PK_HEBERGEUR PRIMARY KEY (idUtilisateur),
  CONSTRAINT FK_HEBERGEUR_1 FOREIGN KEY (idUtilisateur) REFERENCES UTILISATEUR_BACKOFFICE (idUtilisateur)
);

CREATE TABLE FESTIVAL (
  idFestival                       BIGINT NOT NULL,
  nomFestival                      VARCHAR(100) NOT NULL,
  domaine                          VARCHAR(40) NOT NULL,
  sousDomaine                      VARCHAR(70),
  periodicite                      VARCHAR(30),
  moisDebut                        INTEGER NOT NULL,
  siteWebFestival                  VARCHAR(150),
  numIdentification                VARCHAR(50),
  dateCreation                     DATE,
  codePostalFestival               VARCHAR(5) NOT NULL,
  dateDebutAncien                  DATE,
  dateFinAncien                    DATE,
  dateDebutFestival                DATE NOT NULL,
  dateFinFestival                  DATE NOT NULL,
  quotaPass                        INTEGER NOT NULL,
  nbPassVendus                     INTEGER DEFAULT 0 NOT NULL,
  prixPass                         NUMERIC(8,2) NOT NULL,
  actifFestival                    BOOLEAN DEFAULT TRUE NOT NULL,
  codeInsee                        VARCHAR(5) NOT NULL,
  idOrganisateur                   BIGINT,
  CONSTRAINT PK_FESTIVAL PRIMARY KEY (idFestival),
  CONSTRAINT FK_FESTIVAL_1 FOREIGN KEY (codeInsee) REFERENCES COMMUNE (codeInsee),
  CONSTRAINT FK_FESTIVAL_2 FOREIGN KEY (idOrganisateur) REFERENCES ORGANISATEUR (idUtilisateur),
  CONSTRAINT CK_FESTIVAL_1 CHECK (moisDebut BETWEEN 1 AND 12),
  CONSTRAINT CK_FESTIVAL_2 CHECK (dateFinFestival >= dateDebutFestival),
  CONSTRAINT CK_FESTIVAL_3 CHECK (quotaPass >= 0),
  CONSTRAINT CK_FESTIVAL_4 CHECK (nbPassVendus BETWEEN 0 AND quotaPass),
  CONSTRAINT CK_FESTIVAL_5 CHECK (prixPass >= 0),
  CONSTRAINT CK_FESTIVAL_6 CHECK (domaine IN ('MUSIQUES_ACTUELLES', 'CINEMA_ET_AUDIOVISUEL', 'MUSIQUES_CLASSIQUES', 'CIRQUE_ET_ARTS_DE_LA_RUE', 'LIVRE_ET_LITTERATURE', 'DANSE', 'THEATRE', 'ARTS_PLASTIQUES_ET_VISUELS', 'PLURIDISCIPLINAIRE_SPECTACLE_VIVANT', 'PLURIDISCIPLINAIRE_MUSIQUE', 'DIVERS_SPECTACLE_VIVANT', 'TRANSDISCIPLINAIRE', 'DOMAINES_DIVERS')),
  CONSTRAINT CK_FESTIVAL_7 CHECK (sousDomaine IN ('AMPLIFIEES_OU_ELECTRONIQUES', 'JAZZ_BLUES_ET_IMPROVISEES', 'CHANSON', 'TRADITIONNELLES_ET_DU_MONDE', 'BAROQUE_ET_ANCIEN', 'ARTS_DE_LA_RUE')),
  CONSTRAINT CK_FESTIVAL_8 CHECK (periodicite IN ('ANNUELLE', 'BIENNALE_ANNEES_PAIRES', 'BIENNALE_ANNEES_IMPAIRES', 'BIANNUELLE', 'IRREGULIERE'))
);

CREATE TABLE ETABLISSEMENT (
  idEtablissement                  BIGINT NOT NULL,
  nomCommercial                    VARCHAR(80) NOT NULL,
  adresse                          VARCHAR(80) NOT NULL,
  codePostalEtablissement          VARCHAR(5) NOT NULL,
  nomCommuneEtablissement          VARCHAR(50) NOT NULL,
  telephoneEtablissement           VARCHAR(30),
  siteWebEtablissement             VARCHAR(350),
  capaciteAccueil                  INTEGER NOT NULL,
  classement                       VARCHAR(50) NOT NULL,
  dateClassement                   DATE NOT NULL,
  classementProroge                BOOLEAN NOT NULL,
  latitudeEtablissement            NUMERIC(12,9),
  longitudeEtablissement           NUMERIC(12,9),
  noteMoyenne                      NUMERIC(3,2),
  nbNotes                          INTEGER DEFAULT 0 NOT NULL,
  idUtilisateur                    BIGINT,
  CONSTRAINT PK_ETABLISSEMENT PRIMARY KEY (idEtablissement),
  CONSTRAINT FK_ETABLISSEMENT_1 FOREIGN KEY (idUtilisateur) REFERENCES HEBERGEUR (idUtilisateur),
  CONSTRAINT CK_ETABLISSEMENT_1 CHECK (capaciteAccueil > 0),
  CONSTRAINT CK_ETABLISSEMENT_2 CHECK (noteMoyenne BETWEEN 1 AND 5),
  CONSTRAINT CK_ETABLISSEMENT_3 CHECK (nbNotes >= 0),
  CONSTRAINT CK_ETABLISSEMENT_4 CHECK (classement IN ('UNE_ETOILE', 'DEUX_ETOILES', 'TROIS_ETOILES', 'QUATRE_ETOILES', 'CINQ_ETOILES', 'AUBERGE_COLLECTIVE', 'AIRE_NATURELLE'))
);

CREATE TABLE HOTEL_DE_TOURISME (
  idEtablissement                  BIGINT NOT NULL,
  nbChambresHotel                  INTEGER NOT NULL,
  CONSTRAINT PK_HOTEL_DE_TOURISME PRIMARY KEY (idEtablissement),
  CONSTRAINT FK_HOTEL_DE_TOURISME_1 FOREIGN KEY (idEtablissement) REFERENCES ETABLISSEMENT (idEtablissement)
);

CREATE TABLE AUBERGE_COLLECTIVE (
  idEtablissement                  BIGINT NOT NULL,
  nbChambresAuberge                INTEGER NOT NULL,
  CONSTRAINT PK_AUBERGE_COLLECTIVE PRIMARY KEY (idEtablissement),
  CONSTRAINT FK_AUBERGE_COLLECTIVE_1 FOREIGN KEY (idEtablissement) REFERENCES ETABLISSEMENT (idEtablissement)
);

CREATE TABLE CAMPING (
  idEtablissement                  BIGINT NOT NULL,
  categorie                        VARCHAR(10),
  nbEmplacementsCamping            INTEGER NOT NULL,
  CONSTRAINT PK_CAMPING PRIMARY KEY (idEtablissement),
  CONSTRAINT FK_CAMPING_1 FOREIGN KEY (idEtablissement) REFERENCES ETABLISSEMENT (idEtablissement),
  CONSTRAINT CK_CAMPING_1 CHECK (categorie IN ('TOURISME', 'LOISIRS'))
);

CREATE TABLE PARC_RESIDENTIEL_DE_LOISIRS (
  idEtablissement                  BIGINT NOT NULL,
  nbEmplacementsParc               INTEGER NOT NULL,
  CONSTRAINT PK_PARC_RESIDENTIEL_DE_LOISIRS PRIMARY KEY (idEtablissement),
  CONSTRAINT FK_PARC_RESIDENTIEL_DE_LOISI_1 FOREIGN KEY (idEtablissement) REFERENCES ETABLISSEMENT (idEtablissement)
);

CREATE TABLE VILLAGE_DE_VACANCES (
  idEtablissement                  BIGINT NOT NULL,
  mention                          VARCHAR(30),
  typeSejour                       VARCHAR(30),
  nbLogements                      INTEGER NOT NULL,
  CONSTRAINT PK_VILLAGE_DE_VACANCES PRIMARY KEY (idEtablissement),
  CONSTRAINT FK_VILLAGE_DE_VACANCES_1 FOREIGN KEY (idEtablissement) REFERENCES ETABLISSEMENT (idEtablissement),
  CONSTRAINT CK_VILLAGE_DE_VACANCES_1 CHECK (mention IN ('NON', 'HEBERGEMENT_DISPERSE', 'HEBERGEMENT_LEGER', 'HEBERGEMENT_LEGER_ET_DISPERSE')),
  CONSTRAINT CK_VILLAGE_DE_VACANCES_2 CHECK (typeSejour IN ('FORMULE_PENSION', 'FORMULE_LOCATION', 'FORMULE_LOCATION_PENSION'))
);

CREATE TABLE RESIDENCE_DE_TOURISME (
  idEtablissement                  BIGINT NOT NULL,
  nbUnitesHabitation               INTEGER NOT NULL,
  CONSTRAINT PK_RESIDENCE_DE_TOURISME PRIMARY KEY (idEtablissement),
  CONSTRAINT FK_RESIDENCE_DE_TOURISME_1 FOREIGN KEY (idEtablissement) REFERENCES ETABLISSEMENT (idEtablissement)
);

CREATE TABLE OPTION_HEBERGEMENT (
  idOptionHebergement              BIGINT NOT NULL,
  libelleOptionHebergement         VARCHAR(50) NOT NULL,
  CONSTRAINT PK_OPTION_HEBERGEMENT PRIMARY KEY (idOptionHebergement),
  CONSTRAINT UK_OPTION_HEBERGEMENT_1 UNIQUE (libelleOptionHebergement)
);

CREATE TABLE HEBERGEMENT (
  idEtablissement                  BIGINT NOT NULL,
  numeroHebergement                VARCHAR(10) NOT NULL,
  typeHebergement                  VARCHAR(30) NOT NULL,
  capaciteHebergement              INTEGER NOT NULL,
  prixNuitHebergement              NUMERIC(8,2) NOT NULL,
  descriptionHebergement           VARCHAR(500),
  actifHebergement                 BOOLEAN DEFAULT TRUE NOT NULL,
  CONSTRAINT PK_HEBERGEMENT PRIMARY KEY (idEtablissement, numeroHebergement),
  CONSTRAINT FK_HEBERGEMENT_1 FOREIGN KEY (idEtablissement) REFERENCES ETABLISSEMENT (idEtablissement),
  CONSTRAINT CK_HEBERGEMENT_1 CHECK (capaciteHebergement > 0),
  CONSTRAINT CK_HEBERGEMENT_2 CHECK (prixNuitHebergement >= 0),
  CONSTRAINT CK_HEBERGEMENT_3 CHECK (typeHebergement IN ('CHAMBRE_SIMPLE', 'CHAMBRE_DOUBLE', 'EMPLACEMENT_DE_CAMPING', 'BUNGALOW'))
);

CREATE TABLE PHOTO_HEBERGEMENT (
  idPhotoHebergement               BIGINT NOT NULL,
  urlPhotoHebergement              VARCHAR(300) NOT NULL,
  idEtablissement                  BIGINT NOT NULL,
  numeroHebergement                VARCHAR(10) NOT NULL,
  CONSTRAINT PK_PHOTO_HEBERGEMENT PRIMARY KEY (idPhotoHebergement),
  CONSTRAINT FK_PHOTO_HEBERGEMENT_1 FOREIGN KEY (idEtablissement, numeroHebergement) REFERENCES HEBERGEMENT (idEtablissement, numeroHebergement)
);

CREATE TABLE EQUIPEMENT (
  idEtablissement                  BIGINT NOT NULL,
  numeroHebergement                VARCHAR(10) NOT NULL,
  idOptionHebergement              BIGINT NOT NULL,
  CONSTRAINT PK_EQUIPEMENT PRIMARY KEY (idEtablissement, numeroHebergement, idOptionHebergement),
  CONSTRAINT FK_EQUIPEMENT_1 FOREIGN KEY (idEtablissement, numeroHebergement) REFERENCES HEBERGEMENT (idEtablissement, numeroHebergement),
  CONSTRAINT FK_EQUIPEMENT_2 FOREIGN KEY (idOptionHebergement) REFERENCES OPTION_HEBERGEMENT (idOptionHebergement)
);

CREATE TABLE RESERVATION (
  numeroReservation                VARCHAR(20) NOT NULL,
  dateReservation                  TIMESTAMP NOT NULL,
  idUtilisateur                    BIGINT NOT NULL,
  CONSTRAINT PK_RESERVATION PRIMARY KEY (numeroReservation),
  CONSTRAINT FK_RESERVATION_1 FOREIGN KEY (idUtilisateur) REFERENCES FESTIVALIER (idUtilisateur)
);

CREATE TABLE PAIEMENT (
  idPaiement                       BIGINT NOT NULL,
  numTransaction                   VARCHAR(30),
  montantPaiement                  NUMERIC(10,2) NOT NULL,
  datePaiement                     TIMESTAMP,
  statutPaiement                   VARCHAR(20) NOT NULL,
  numeroReservation                VARCHAR(20) NOT NULL,
  CONSTRAINT PK_PAIEMENT PRIMARY KEY (idPaiement),
  CONSTRAINT UK_PAIEMENT_1 UNIQUE (numTransaction),
  CONSTRAINT UK_PAIEMENT_2 UNIQUE (numeroReservation),
  CONSTRAINT FK_PAIEMENT_1 FOREIGN KEY (numeroReservation) REFERENCES RESERVATION (numeroReservation),
  CONSTRAINT CK_PAIEMENT_1 CHECK (montantPaiement >= 0),
  CONSTRAINT CK_PAIEMENT_2 CHECK (statutPaiement IN ('NON_GERE', 'EN_ATTENTE', 'ACCEPTE', 'REFUSE', 'REMBOURSE'))
);

CREATE TABLE SELECTION (
  idSelection                      BIGINT NOT NULL,
  prixPassSelection                NUMERIC(8,2) NOT NULL,
  statutSelection                  VARCHAR(20) NOT NULL,
  numeroReservation                VARCHAR(20) NOT NULL,
  idFestival                       BIGINT NOT NULL,
  CONSTRAINT PK_SELECTION PRIMARY KEY (idSelection),
  CONSTRAINT UK_SELECTION_1 UNIQUE (numeroReservation, idFestival),
  CONSTRAINT FK_SELECTION_1 FOREIGN KEY (numeroReservation) REFERENCES RESERVATION (numeroReservation),
  CONSTRAINT FK_SELECTION_2 FOREIGN KEY (idFestival) REFERENCES FESTIVAL (idFestival),
  CONSTRAINT CK_SELECTION_1 CHECK (prixPassSelection >= 0),
  CONSTRAINT CK_SELECTION_2 CHECK (statutSelection IN ('CONFIRMEE', 'ANNULEE'))
);

CREATE TABLE PASS (
  idPass                           BIGINT NOT NULL,
  codePass                         VARCHAR(40) NOT NULL,
  idSelection                      BIGINT NOT NULL,
  CONSTRAINT PK_PASS PRIMARY KEY (idPass),
  CONSTRAINT UK_PASS_1 UNIQUE (codePass),
  CONSTRAINT FK_PASS_1 FOREIGN KEY (idSelection) REFERENCES SELECTION (idSelection)
);

CREATE TABLE NUITEE (
  idEtablissement                  BIGINT NOT NULL,
  numeroHebergement                VARCHAR(10) NOT NULL,
  dateNuitee                       DATE NOT NULL,
  prixNuitee                       NUMERIC(8,2) NOT NULL,
  idSelection                      BIGINT,
  CONSTRAINT PK_NUITEE PRIMARY KEY (idEtablissement, numeroHebergement, dateNuitee),
  CONSTRAINT FK_NUITEE_1 FOREIGN KEY (idEtablissement, numeroHebergement) REFERENCES HEBERGEMENT (idEtablissement, numeroHebergement),
  CONSTRAINT FK_NUITEE_2 FOREIGN KEY (idSelection) REFERENCES SELECTION (idSelection),
  CONSTRAINT CK_NUITEE_1 CHECK (prixNuitee >= 0)
);

CREATE TABLE NOTATION_FESTIVAL (
  idFestival                       BIGINT NOT NULL,
  idUtilisateur                    BIGINT NOT NULL,
  noteFestival                     INTEGER NOT NULL,
  dateNoteFestival                 DATE NOT NULL,
  CONSTRAINT PK_NOTATION_FESTIVAL PRIMARY KEY (idFestival, idUtilisateur),
  CONSTRAINT FK_NOTATION_FESTIVAL_1 FOREIGN KEY (idFestival) REFERENCES FESTIVAL (idFestival),
  CONSTRAINT FK_NOTATION_FESTIVAL_2 FOREIGN KEY (idUtilisateur) REFERENCES FESTIVALIER (idUtilisateur),
  CONSTRAINT CK_NOTATION_FESTIVAL_1 CHECK (noteFestival BETWEEN 1 AND 5)
);

CREATE TABLE NOTATION_ETABLISSEMENT (
  idEtablissement                  BIGINT NOT NULL,
  idUtilisateur                    BIGINT NOT NULL,
  noteEtablissement                INTEGER NOT NULL,
  dateNoteEtablissement            DATE NOT NULL,
  CONSTRAINT PK_NOTATION_ETABLISSEMENT PRIMARY KEY (idEtablissement, idUtilisateur),
  CONSTRAINT FK_NOTATION_ETABLISSEMENT_1 FOREIGN KEY (idEtablissement) REFERENCES ETABLISSEMENT (idEtablissement),
  CONSTRAINT FK_NOTATION_ETABLISSEMENT_2 FOREIGN KEY (idUtilisateur) REFERENCES FESTIVALIER (idUtilisateur),
  CONSTRAINT CK_NOTATION_ETABLISSEMENT_1 CHECK (noteEtablissement BETWEEN 1 AND 5)
);

-- Index : Oracle n'indexe pas automatiquement les clés étrangères.
CREATE INDEX IX_DEPARTEMENT_1 ON DEPARTEMENT (idRegion);
CREATE INDEX IX_COMMUNE_1 ON COMMUNE (codeDepartement);
CREATE INDEX IX_FESTIVAL_1 ON FESTIVAL (dateDebutFestival, dateFinFestival);
CREATE INDEX IX_FESTIVAL_2 ON FESTIVAL (codeInsee);
CREATE INDEX IX_FESTIVAL_3 ON FESTIVAL (domaine);
CREATE INDEX IX_FESTIVAL_4 ON FESTIVAL (idOrganisateur);
CREATE INDEX IX_ETABLISSEMENT_1 ON ETABLISSEMENT (latitudeEtablissement, longitudeEtablissement);
CREATE INDEX IX_ETABLISSEMENT_2 ON ETABLISSEMENT (codePostalEtablissement);
CREATE INDEX IX_ETABLISSEMENT_3 ON ETABLISSEMENT (idUtilisateur);
CREATE INDEX IX_PHOTO_HEBERGEMENT_1 ON PHOTO_HEBERGEMENT (idEtablissement, numeroHebergement);
CREATE INDEX IX_EQUIPEMENT_1 ON EQUIPEMENT (idOptionHebergement);
CREATE INDEX IX_RESERVATION_1 ON RESERVATION (idUtilisateur);
CREATE INDEX IX_SELECTION_1 ON SELECTION (idFestival);
CREATE INDEX IX_PASS_1 ON PASS (idSelection);
CREATE INDEX IX_NUITEE_1 ON NUITEE (dateNuitee, idSelection);
CREATE INDEX IX_NUITEE_2 ON NUITEE (idSelection);
CREATE INDEX IX_NOTATION_FESTIVAL_1 ON NOTATION_FESTIVAL (idUtilisateur);
CREATE INDEX IX_NOTATION_ETABLISSEMENT_1 ON NOTATION_ETABLISSEMENT (idUtilisateur);
