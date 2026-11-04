package fr.uga.miage.m1.festibed.repositories

import fr.uga.miage.m1.festibed.data.entities.CampingEntity
import fr.uga.miage.m1.festibed.data.entities.CommuneEntity
import fr.uga.miage.m1.festibed.data.entities.DepartementEntity
import fr.uga.miage.m1.festibed.data.entities.FestivalEntity
import fr.uga.miage.m1.festibed.data.entities.FestivalierEntity
import fr.uga.miage.m1.festibed.data.entities.HebergementEntity
import fr.uga.miage.m1.festibed.data.entities.NuiteeEntity
import fr.uga.miage.m1.festibed.data.entities.RegionEntity
import fr.uga.miage.m1.festibed.enums.Classement
import fr.uga.miage.m1.festibed.enums.Domaine
import fr.uga.miage.m1.festibed.enums.TypeHebergement
import jakarta.persistence.EntityManager
import java.math.BigDecimal
import java.time.LocalDate

/** Petit jeu de données commun aux tests de repositories (persisté avec l'EntityManager du test). */
class Jeu(private val em: EntityManager) {

    val commune: CommuneEntity by lazy {
        val region = persister(RegionEntity(nom = "Auvergne-Rhône-Alpes"))
        val departement = persister(DepartementEntity(code = "73", nom = "Savoie", region = region))
        persister(
            CommuneEntity(
                codeInsee = "73008", nom = "AIX LES BAINS", latitude = BigDecimal("45.697854168"),
                longitude = BigDecimal("5.903886270"), departement = departement,
            ),
        )
    }

    fun festival(nom: String = "Musilac", quota: Int = 40, debut: LocalDate = LocalDate.of(2027, 7, 12)) = persister(
        FestivalEntity(
            nom = nom, domaine = Domaine.MUSIQUES_ACTUELLES, codePostal = "73100", dateDebut = debut,
            dateFin = debut.plusDays(3), quotaPass = quota, prixPass = BigDecimal("100.00"), commune = commune,
        ),
    )

    fun festivalier(email: String = "camille@festibed.test") =
        persister(FestivalierEntity(nom = "Camille", email = email))

    fun camping(osmRef: String = "node/1") = persister(
        CampingEntity(
            nomCommercial = "CAMPING DU SIERROZ", codePostal = "73100", nomCommune = "AIX-LES-BAINS", commune = commune,
            capaciteAccueil = 300, classement = Classement.TROIS_ETOILES, dateClassement = LocalDate.of(2026, 6, 30),
            latitude = BigDecimal("45.700404972"), longitude = BigDecimal("5.887147489"), osmRef = osmRef, nbEmplacements = 149,
        ),
    )

    fun hebergement(numero: String = "H001", capacite: Int = 2) = persister(
        HebergementEntity(
            etablissement = camping("node/$numero"), numero = numero, typeHebergement = TypeHebergement.BUNGALOW,
            capacite = capacite, prixNuit = BigDecimal("50.00"),
        ),
    )

    fun nuits(h: HebergementEntity, du: LocalDate, nombre: Int) = (0 until nombre).map {
        persister(NuiteeEntity(hebergement = h, dateNuitee = du.plusDays(it.toLong()), prix = h.prixNuit))
    }

    fun <T : Any> persister(entite: T): T {
        em.persist(entite)
        em.flush()
        return entite
    }
}
