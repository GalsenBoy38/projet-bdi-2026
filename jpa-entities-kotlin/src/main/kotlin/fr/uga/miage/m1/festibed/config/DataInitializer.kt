package fr.uga.miage.m1.festibed.config

import fr.uga.miage.m1.festibed.data.entities.CampingEntity
import fr.uga.miage.m1.festibed.data.entities.CommuneEntity
import fr.uga.miage.m1.festibed.data.entities.DepartementEntity
import fr.uga.miage.m1.festibed.data.entities.EtablissementEntity
import fr.uga.miage.m1.festibed.data.entities.EtablissementNonClasseEntity
import fr.uga.miage.m1.festibed.data.entities.FestivalEntity
import fr.uga.miage.m1.festibed.data.entities.FestivalierEntity
import fr.uga.miage.m1.festibed.data.entities.HebergementEntity
import fr.uga.miage.m1.festibed.data.entities.HebergeurEntity
import fr.uga.miage.m1.festibed.data.entities.HotelDeTourismeEntity
import fr.uga.miage.m1.festibed.data.entities.NotationEtablissementEntity
import fr.uga.miage.m1.festibed.data.entities.NotationFestivalEntity
import fr.uga.miage.m1.festibed.data.entities.NuiteeEntity
import fr.uga.miage.m1.festibed.data.entities.OptionHebergementEntity
import fr.uga.miage.m1.festibed.data.entities.OrganisateurEntity
import fr.uga.miage.m1.festibed.data.entities.PaiementEntity
import fr.uga.miage.m1.festibed.data.entities.PassEntity
import fr.uga.miage.m1.festibed.data.entities.PhotoHebergementEntity
import fr.uga.miage.m1.festibed.data.entities.RegionEntity
import fr.uga.miage.m1.festibed.data.entities.ReservationEntity
import fr.uga.miage.m1.festibed.data.entities.SelectionEntity
import fr.uga.miage.m1.festibed.data.repositories.CommuneRepository
import fr.uga.miage.m1.festibed.data.repositories.DepartementRepository
import fr.uga.miage.m1.festibed.data.repositories.EtablissementRepository
import fr.uga.miage.m1.festibed.data.repositories.FestivalRepository
import fr.uga.miage.m1.festibed.data.repositories.FestivalierRepository
import fr.uga.miage.m1.festibed.data.repositories.HebergementRepository
import fr.uga.miage.m1.festibed.data.repositories.HebergeurRepository
import fr.uga.miage.m1.festibed.data.repositories.NotationEtablissementRepository
import fr.uga.miage.m1.festibed.data.repositories.NotationFestivalRepository
import fr.uga.miage.m1.festibed.data.repositories.NuiteeRepository
import fr.uga.miage.m1.festibed.data.repositories.OptionHebergementRepository
import fr.uga.miage.m1.festibed.data.repositories.OrganisateurRepository
import fr.uga.miage.m1.festibed.data.repositories.PaiementRepository
import fr.uga.miage.m1.festibed.data.repositories.RegionRepository
import fr.uga.miage.m1.festibed.data.repositories.ReservationRepository
import fr.uga.miage.m1.festibed.enums.CategorieCamping
import fr.uga.miage.m1.festibed.enums.Classement
import fr.uga.miage.m1.festibed.enums.Domaine
import fr.uga.miage.m1.festibed.enums.Periodicite
import fr.uga.miage.m1.festibed.enums.SousDomaine
import fr.uga.miage.m1.festibed.enums.TypeHebergement
import fr.uga.miage.m1.festibed.enums.TypeNonClasse
import org.springframework.boot.ApplicationArguments
import org.springframework.boot.ApplicationRunner
import org.springframework.context.annotation.Profile
import org.springframework.stereotype.Component
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.LocalDate
import java.time.LocalDateTime

/**
 * Données de démonstration des scénarios du cahier des charges (édition 2027) :
 *  - scénario 1 : Musilac à Aix-les-Bains + camping international du Sierroz ;
 *  - scénarios 2 et 3 : Jazz à Couches et Saint Rock + hôtel des Arcades à Autun ;
 *  - scénario 4 : Ronald, organisateur (mot de passe « festibed », haché en BCrypt).
 * Tout passe par les repositories : Hibernate crée le schéma, aucun script SQL.
 */
@Component
@Profile("!test")
class DataInitializer(
    private val regionRepository: RegionRepository,
    private val departementRepository: DepartementRepository,
    private val communeRepository: CommuneRepository,
    private val organisateurRepository: OrganisateurRepository,
    private val hebergeurRepository: HebergeurRepository,
    private val festivalierRepository: FestivalierRepository,
    private val festivalRepository: FestivalRepository,
    private val etablissementRepository: EtablissementRepository,
    private val optionHebergementRepository: OptionHebergementRepository,
    private val hebergementRepository: HebergementRepository,
    private val nuiteeRepository: NuiteeRepository,
    private val reservationRepository: ReservationRepository,
    private val paiementRepository: PaiementRepository,
    private val notationFestivalRepository: NotationFestivalRepository,
    private val notationEtablissementRepository: NotationEtablissementRepository,
) : ApplicationRunner {

    @Transactional
    override fun run(args: ApplicationArguments) {
        if (festivalRepository.count() > 0) return

        // ---- géographie
        val ara = regionRepository.save(RegionEntity(nom = "Auvergne-Rhône-Alpes"))
        val bfc = regionRepository.save(RegionEntity(nom = "Bourgogne-Franche-Comté"))
        val savoie = departementRepository.save(DepartementEntity(code = "73", nom = "Savoie", region = ara))
        val saoneEtLoire = departementRepository.save(DepartementEntity(code = "71", nom = "Saône-et-Loire", region = bfc))
        val aix = communeRepository.save(commune("73008", "AIX LES BAINS", "45.697854168", "5.903886270", savoie))
        val couches = communeRepository.save(commune("71149", "COUCHES", "46.869155076", "4.564315984", saoneEtLoire))
        val laClayette = communeRepository.save(commune("71133", "LA CLAYETTE", "46.289294432", "4.310799671", saoneEtLoire))
        val autun = communeRepository.save(commune("71014", "AUTUN", "46.945536773", "4.310600695", saoneEtLoire))

        // ---- utilisateurs
        val ronald = organisateurRepository.save(
            OrganisateurEntity(nom = "Ronald Organisateur", email = "ronald.organisateur@festibed.test", motDePasseHache = HASH_FESTIBED),
        )
        val hebergeur = hebergeurRepository.save(
            HebergeurEntity(nom = "Hébergeur Démonstration", email = "hebergeur.demo@festibed.test", motDePasseHache = HASH_FESTIBED),
        )
        val festivaliers = festivalierRepository.saveAll(
            listOf(
                FestivalierEntity(nom = "Camille Martin", email = "camille.martin@festibed.test", fournisseurAuth = "GOOGLE", identifiantExterne = "g-1001"),
                FestivalierEntity(nom = "Lucas Bernard", email = "lucas.bernard@festibed.test", fournisseurAuth = "FACEBOOK", identifiantExterne = "f-2002"),
                FestivalierEntity(nom = "Inès Petit", email = "ines.petit@festibed.test"),
            ),
        )

        // ---- festivals
        val musilac = festivalRepository.save(
            FestivalEntity(
                nom = "Musilac", domaine = Domaine.MUSIQUES_ACTUELLES, sousDomaine = SousDomaine.AMPLIFIEES_OU_ELECTRONIQUES,
                periodicite = Periodicite.ANNUELLE, siteWeb = "www.musilac.com", dateCreation = LocalDate.of(2002, 1, 1),
                codePostal = "73100", dateDebut = LocalDate.of(2027, 7, 12), dateFin = LocalDate.of(2027, 7, 15),
                quotaPass = 78, prixPass = BigDecimal("163.50"), commune = aix, organisateur = ronald,
            ),
        )
        val jazzACouches = festivalRepository.save(
            FestivalEntity(
                nom = "JAZZ A COUCHES", domaine = Domaine.MUSIQUES_ACTUELLES, sousDomaine = SousDomaine.JAZZ_BLUES_ET_IMPROVISEES,
                periodicite = Periodicite.ANNUELLE, siteWeb = "https://www.jazzacouches.fr/", dateCreation = LocalDate.of(1987, 1, 1),
                codePostal = "71490", dateDebut = LocalDate.of(2027, 7, 4), dateFin = LocalDate.of(2027, 7, 7),
                quotaPass = 46, prixPass = BigDecimal("111.50"), commune = couches, organisateur = ronald,
            ),
        )
        festivalRepository.save(
            FestivalEntity(
                nom = "SAINT ROCK", domaine = Domaine.MUSIQUES_ACTUELLES, sousDomaine = SousDomaine.AMPLIFIEES_OU_ELECTRONIQUES,
                periodicite = Periodicite.ANNUELLE, siteWeb = "www.saintrock.eu", dateCreation = LocalDate.of(2009, 1, 1),
                codePostal = "71800", dateDebut = LocalDate.of(2027, 7, 13), dateFin = LocalDate.of(2027, 7, 14),
                quotaPass = 61, prixPass = BigDecimal("63.50"), commune = laClayette,
            ),
        )

        // ---- établissements (héritage JOINED : une sous-classe par typologie)
        val sierroz = etablissementRepository.save(
            CampingEntity(
                nomCommercial = "CAMPING INTERNATIONAL DU SIERROZ", adresse = "Boulevard Barrier", codePostal = "73100",
                nomCommune = "AIX-LES-BAINS", commune = aix, siteWeb = "https://www.camping-sierroz.com/", capaciteAccueil = 447,
                classement = Classement.TROIS_ETOILES, dateClassement = LocalDate.of(2026, 6, 30),
                latitude = BigDecimal("45.700404972"), longitude = BigDecimal("5.887147489"), osmRef = "node/175590387",
                hebergeur = hebergeur, nbEmplacements = 149, categorie = CategorieCamping.TOURISME,
            ),
        )
        val arcades = etablissementRepository.save(
            HotelDeTourismeEntity(
                nomCommercial = "HÔTEL DES ARCADES", adresse = "22 avenue de la République", codePostal = "71400",
                nomCommune = "AUTUN", commune = autun, telephone = "+33 3 85 52 30 03", email = "lesarcades71@orange.fr",
                siteWeb = "https://terminus.hotel-autun.fr/", capaciteAccueil = 72, classement = Classement.DEUX_ETOILES,
                dateClassement = LocalDate.of(2021, 12, 1), latitude = BigDecimal("46.954468766"),
                longitude = BigDecimal("4.293593146"), osmRef = "node/3260711062", hebergeur = hebergeur, nbChambres = 29,
            ),
        )
        val auberge = etablissementRepository.save(
            EtablissementNonClasseEntity(
                nomCommercial = "Auberge de Jeunesse", adresse = "4 Promenade du Sierroz", codePostal = "73100",
                nomCommune = "Aix-les-Bains", commune = aix, capaciteAccueil = 40, latitude = BigDecimal("45.700667445"),
                longitude = BigDecimal("5.888935013"), osmRef = "node/81914330", typeNonClasse = TypeNonClasse.AUBERGE_DE_JEUNESSE,
            ),
        )

        // ---- options (@ManyToMany via la table « equipement ») et hébergements
        val options = optionHebergementRepository.saveAll(
            listOf("Wi-Fi", "Parking", "Accès PMR", "Petit-déjeuner inclus", "Climatisation", "Animaux acceptés", "Piscine", "Linge fourni")
                .map { OptionHebergementEntity(libelle = it) },
        ).associateBy { it.libelle }

        fun hebergement(
            etablissement: EtablissementEntity, numero: String, type: TypeHebergement, capacite: Int, prix: String,
            description: String, vararg libellesOptions: String,
        ) = hebergementRepository.save(
            HebergementEntity(
                etablissement = etablissement, numero = numero, typeHebergement = type, capacite = capacite,
                prixNuit = BigDecimal(prix), description = description,
                photos = mutableListOf(PhotoHebergementEntity(url = "https://photos.festibed.test/${etablissement.osmRef}/$numero.jpg")),
                options = libellesOptions.map { options.getValue(it) }.toMutableSet(),
            ),
        )

        val sierrozH001 = hebergement(sierroz, "H001", TypeHebergement.EMPLACEMENT_DE_CAMPING, 2, "23.00", "Emplacement de camping pour 2 personnes", "Wi-Fi", "Animaux acceptés")
        val sierrozH002 = hebergement(sierroz, "H002", TypeHebergement.BUNGALOW, 4, "68.00", "Bungalow 4 personnes", "Wi-Fi", "Parking", "Piscine")
        val arcadesH001 = hebergement(arcades, "H001", TypeHebergement.CHAMBRE_SIMPLE, 1, "67.00", "Chambre simple pour 1 personne", "Wi-Fi", "Petit-déjeuner inclus")
        val arcadesH002 = hebergement(arcades, "H002", TypeHebergement.CHAMBRE_DOUBLE, 2, "82.00", "Chambre double", "Wi-Fi", "Parking", "Petit-déjeuner inclus", "Accès PMR")
        val aubergeH001 = hebergement(auberge, "H001", TypeHebergement.LIT_EN_DORTOIR, 1, "29.00", "Lit en dortoir de 6", "Wi-Fi", "Linge fourni")

        // ---- nuitées proposées autour des festivals (une ligne par hébergement et par nuit)
        fun proposer(h: HebergementEntity, du: LocalDate, au: LocalDate) =
            nuiteeRepository.saveAll(
                generateSequence(du) { it.plusDays(1) }.takeWhile { !it.isAfter(au) }
                    .map { NuiteeEntity(hebergement = h, dateNuitee = it, prix = h.prixNuit) }.toList(),
            )
        listOf(sierrozH001, sierrozH002, aubergeH001).forEach { proposer(it, LocalDate.of(2027, 7, 10), LocalDate.of(2027, 7, 16)) }
        listOf(arcadesH001, arcadesH002).forEach { proposer(it, LocalDate.of(2027, 7, 3), LocalDate.of(2027, 7, 15)) }

        // ---- une réservation validée : 2 Pass Musilac + bungalow du Sierroz, 3 nuits
        val camille = festivaliers.first()
        val selection = SelectionEntity(
            festival = musilac, prixPass = musilac.prixPass,
            passes = mutableListOf(PassEntity(code = "FB-MUSILAC-0001"), PassEntity(code = "FB-MUSILAC-0002")),
        )
        val reservation = reservationRepository.save(
            ReservationEntity(numero = "FB7K2M9QX4TA", dateReservation = LocalDateTime.of(2027, 3, 2, 10, 15), festivalier = camille, selections = mutableListOf(selection)),
        )
        val nuits = listOf(LocalDate.of(2027, 7, 12), LocalDate.of(2027, 7, 13), LocalDate.of(2027, 7, 14))
        check(festivalRepository.reserverPass(musilac.id!!, 2) == 1) { "Plus assez de Pass Musilac" }
        check(nuiteeRepository.occuper(reservation.selections.first(), sierrozH002.id!!, nuits) == nuits.size) { "Nuits déjà prises" }
        paiementRepository.save(
            PaiementEntity(reservation = reservation, montant = musilac.prixPass * BigDecimal(2) + sierrozH002.prixNuit * BigDecimal(nuits.size)),
        )

        // ---- notations (la moyenne de l'établissement est tenue à jour par un UPDATE atomique)
        notationFestivalRepository.save(NotationFestivalEntity(festival = jazzACouches, festivalier = festivaliers[1], note = 5, dateNote = LocalDate.of(2026, 7, 10)))
        notationEtablissementRepository.save(NotationEtablissementEntity(etablissement = arcades, festivalier = festivaliers[1], note = 4, dateNote = LocalDate.of(2026, 7, 10)))
        etablissementRepository.ajouterNote(arcades.id!!, BigDecimal(4))
    }

    private fun commune(code: String, nom: String, lat: String, lon: String, departement: DepartementEntity) =
        CommuneEntity(codeInsee = code, nom = nom, latitude = BigDecimal(lat), longitude = BigDecimal(lon), departement = departement)

    companion object {
        /** BCrypt (coût 10) du mot de passe de démonstration « festibed ». */
        const val HASH_FESTIBED = "\$2b\$10\$JB2cWzXA3tTdKo7X63.kduGcMWfHUas5Zv8VPyJ55m1jjK0Qnv1Ze"
    }
}
