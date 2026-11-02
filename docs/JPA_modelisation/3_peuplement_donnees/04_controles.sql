-- FestiBed - Groupe 3 - Contrôles après chargement (Oracle et H2).
-- Chaque requête « anomalies » doit renvoyer 0.

-- 1. Volumes (au moins 100 000 réservations)
SELECT 'reservations' AS controle, COUNT(*) AS valeur FROM RESERVATION;
SELECT 'pass' AS controle, COUNT(*) AS valeur FROM PASS;
SELECT 'nuitees libres' AS controle, COUNT(*) AS valeur FROM NUITEE WHERE idSelection IS NULL;

-- 2. Quota : au moins 30 Pass par festival
SELECT 'anomalies quota < 30' AS controle, COUNT(*) AS valeur FROM FESTIVAL WHERE quotaPass < 30;

-- 3. Compteur nbPassVendus = nombre réel de Pass
SELECT 'anomalies nbPassVendus' AS controle, COUNT(*) AS valeur
FROM FESTIVAL f
WHERE f.nbPassVendus <> (SELECT COUNT(*) FROM PASS p JOIN SELECTION s ON s.idSelection = p.idSelection
                         WHERE s.idFestival = f.idFestival);

-- 4. Au moins la moitié du quota réservée, jamais plus que le quota
SELECT 'anomalies moitie du quota' AS controle, COUNT(*) AS valeur
FROM FESTIVAL WHERE nbPassVendus * 2 < quotaPass OR nbPassVendus > quotaPass;

-- 5. Réservation groupée : chaque sélection a au moins une nuitée, et chaque nuit la capacité couvre les Pass
SELECT 'anomalies selection sans nuitee' AS controle, COUNT(*) AS valeur
FROM SELECTION s WHERE NOT EXISTS (SELECT 1 FROM NUITEE n WHERE n.idSelection = s.idSelection);

SELECT 'anomalies capacite < pass' AS controle, COUNT(*) AS valeur
FROM (SELECT n.idSelection, n.dateNuitee, SUM(h.capaciteHebergement) AS capacite
      FROM NUITEE n JOIN HEBERGEMENT h
        ON h.idEtablissement = n.idEtablissement AND h.numeroHebergement = n.numeroHebergement
      WHERE n.idSelection IS NOT NULL
      GROUP BY n.idSelection, n.dateNuitee) c
WHERE c.capacite < (SELECT COUNT(*) FROM PASS p WHERE p.idSelection = c.idSelection);

-- 6. Les nuitées réservées sont des nuits du festival de la sélection
SELECT 'anomalies nuitee hors festival' AS controle, COUNT(*) AS valeur
FROM NUITEE n JOIN SELECTION s ON s.idSelection = n.idSelection JOIN FESTIVAL f ON f.idFestival = s.idFestival
WHERE n.dateNuitee < f.dateDebutFestival OR n.dateNuitee > f.dateFinFestival;

-- 7. Chaque établissement a exactement un sous-type (héritage JOINED)
SELECT 'anomalies sous-type' AS controle, COUNT(*) AS valeur
FROM ETABLISSEMENT e
WHERE (SELECT COUNT(*) FROM HOTEL_DE_TOURISME x WHERE x.idEtablissement = e.idEtablissement)
    + (SELECT COUNT(*) FROM AUBERGE_COLLECTIVE x WHERE x.idEtablissement = e.idEtablissement)
    + (SELECT COUNT(*) FROM CAMPING x WHERE x.idEtablissement = e.idEtablissement)
    + (SELECT COUNT(*) FROM PARC_RESIDENTIEL_DE_LOISIRS x WHERE x.idEtablissement = e.idEtablissement)
    + (SELECT COUNT(*) FROM VILLAGE_DE_VACANCES x WHERE x.idEtablissement = e.idEtablissement)
    + (SELECT COUNT(*) FROM RESIDENCE_DE_TOURISME x WHERE x.idEtablissement = e.idEtablissement) <> 1;

-- 8. Chaque utilisateur a exactement un rôle
SELECT 'anomalies role utilisateur' AS controle, COUNT(*) AS valeur
FROM UTILISATEUR u
WHERE (SELECT COUNT(*) FROM FESTIVALIER x WHERE x.idUtilisateur = u.idUtilisateur)
    + (SELECT COUNT(*) FROM ORGANISATEUR x WHERE x.idUtilisateur = u.idUtilisateur)
    + (SELECT COUNT(*) FROM HEBERGEUR x WHERE x.idUtilisateur = u.idUtilisateur) <> 1;

-- 9. Note moyenne dénormalisée cohérente
SELECT 'anomalies nbNotes' AS controle, COUNT(*) AS valeur
FROM ETABLISSEMENT e
WHERE e.nbNotes <> (SELECT COUNT(*) FROM NOTATION_ETABLISSEMENT n WHERE n.idEtablissement = e.idEtablissement);

-- 10. Festivals qui se chevauchent dans un même département (doit être > 0)
SELECT 'festivals qui se chevauchent' AS controle, COUNT(*) AS valeur
FROM FESTIVAL a JOIN FESTIVAL b ON a.idFestival < b.idFestival
 AND SUBSTR(a.codeInsee, 1, 2) = SUBSTR(b.codeInsee, 1, 2)
 AND a.dateDebutFestival <= b.dateFinFestival AND b.dateDebutFestival <= a.dateFinFestival;

-- 11. Établissements non géocodés (information)
SELECT 'etablissements sans coordonnees' AS controle, COUNT(*) AS valeur
FROM ETABLISSEMENT WHERE latitudeEtablissement IS NULL;
