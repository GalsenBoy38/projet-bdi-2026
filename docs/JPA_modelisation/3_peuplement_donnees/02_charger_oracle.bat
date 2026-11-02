@echo off
REM FestiBed - chargement Oracle par SQL*Loader (ordre des clés étrangères)
REM Usage : 02_charger_oracle.bat utilisateur/motdepasse@//hote:1521/service
set NLS_LANG=AMERICAN_AMERICA.AL32UTF8
cd /d %~dp0
if not exist logs mkdir logs
sqlldr userid=%1 control=sqlldr\01_REGION.ctl log=logs\REGION.log bad=logs\REGION.bad || goto erreur
sqlldr userid=%1 control=sqlldr\02_DEPARTEMENT.ctl log=logs\DEPARTEMENT.log bad=logs\DEPARTEMENT.bad || goto erreur
sqlldr userid=%1 control=sqlldr\03_COMMUNE.ctl log=logs\COMMUNE.log bad=logs\COMMUNE.bad || goto erreur
sqlldr userid=%1 control=sqlldr\04_UTILISATEUR.ctl log=logs\UTILISATEUR.log bad=logs\UTILISATEUR.bad || goto erreur
sqlldr userid=%1 control=sqlldr\05_FESTIVALIER.ctl log=logs\FESTIVALIER.log bad=logs\FESTIVALIER.bad || goto erreur
sqlldr userid=%1 control=sqlldr\06_UTILISATEUR_BACKOFFICE.ctl log=logs\UTILISATEUR_BACKOFFICE.log bad=logs\UTILISATEUR_BACKOFFICE.bad || goto erreur
sqlldr userid=%1 control=sqlldr\07_ORGANISATEUR.ctl log=logs\ORGANISATEUR.log bad=logs\ORGANISATEUR.bad || goto erreur
sqlldr userid=%1 control=sqlldr\08_HEBERGEUR.ctl log=logs\HEBERGEUR.log bad=logs\HEBERGEUR.bad || goto erreur
sqlldr userid=%1 control=sqlldr\09_FESTIVAL.ctl log=logs\FESTIVAL.log bad=logs\FESTIVAL.bad || goto erreur
sqlldr userid=%1 control=sqlldr\10_ETABLISSEMENT.ctl log=logs\ETABLISSEMENT.log bad=logs\ETABLISSEMENT.bad || goto erreur
sqlldr userid=%1 control=sqlldr\11_HOTEL_DE_TOURISME.ctl log=logs\HOTEL_DE_TOURISME.log bad=logs\HOTEL_DE_TOURISME.bad || goto erreur
sqlldr userid=%1 control=sqlldr\12_AUBERGE_COLLECTIVE.ctl log=logs\AUBERGE_COLLECTIVE.log bad=logs\AUBERGE_COLLECTIVE.bad || goto erreur
sqlldr userid=%1 control=sqlldr\13_CAMPING.ctl log=logs\CAMPING.log bad=logs\CAMPING.bad || goto erreur
sqlldr userid=%1 control=sqlldr\14_PARC_RESIDENTIEL_DE_LOISIRS.ctl log=logs\PARC_RESIDENTIEL_DE_LOISIRS.log bad=logs\PARC_RESIDENTIEL_DE_LOISIRS.bad || goto erreur
sqlldr userid=%1 control=sqlldr\15_VILLAGE_DE_VACANCES.ctl log=logs\VILLAGE_DE_VACANCES.log bad=logs\VILLAGE_DE_VACANCES.bad || goto erreur
sqlldr userid=%1 control=sqlldr\16_RESIDENCE_DE_TOURISME.ctl log=logs\RESIDENCE_DE_TOURISME.log bad=logs\RESIDENCE_DE_TOURISME.bad || goto erreur
sqlldr userid=%1 control=sqlldr\17_OPTION_HEBERGEMENT.ctl log=logs\OPTION_HEBERGEMENT.log bad=logs\OPTION_HEBERGEMENT.bad || goto erreur
sqlldr userid=%1 control=sqlldr\18_HEBERGEMENT.ctl log=logs\HEBERGEMENT.log bad=logs\HEBERGEMENT.bad || goto erreur
sqlldr userid=%1 control=sqlldr\19_PHOTO_HEBERGEMENT.ctl log=logs\PHOTO_HEBERGEMENT.log bad=logs\PHOTO_HEBERGEMENT.bad || goto erreur
sqlldr userid=%1 control=sqlldr\20_EQUIPEMENT.ctl log=logs\EQUIPEMENT.log bad=logs\EQUIPEMENT.bad || goto erreur
sqlldr userid=%1 control=sqlldr\21_RESERVATION.ctl log=logs\RESERVATION.log bad=logs\RESERVATION.bad || goto erreur
sqlldr userid=%1 control=sqlldr\22_PAIEMENT.ctl log=logs\PAIEMENT.log bad=logs\PAIEMENT.bad || goto erreur
sqlldr userid=%1 control=sqlldr\23_SELECTION.ctl log=logs\SELECTION.log bad=logs\SELECTION.bad || goto erreur
sqlldr userid=%1 control=sqlldr\24_PASS.ctl log=logs\PASS.log bad=logs\PASS.bad || goto erreur
sqlldr userid=%1 control=sqlldr\25_NUITEE.ctl log=logs\NUITEE.log bad=logs\NUITEE.bad || goto erreur
sqlldr userid=%1 control=sqlldr\26_NOTATION_FESTIVAL.ctl log=logs\NOTATION_FESTIVAL.log bad=logs\NOTATION_FESTIVAL.bad || goto erreur
sqlldr userid=%1 control=sqlldr\27_NOTATION_ETABLISSEMENT.ctl log=logs\NOTATION_ETABLISSEMENT.log bad=logs\NOTATION_ETABLISSEMENT.bad || goto erreur
echo Chargement termine. Executer ensuite 03_sequences_oracle.sql puis 04_controles.sql.
exit /b 0
:erreur
echo ECHEC : voir le dossier logs
exit /b 1
