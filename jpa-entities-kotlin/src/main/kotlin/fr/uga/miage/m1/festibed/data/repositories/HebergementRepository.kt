package fr.uga.miage.m1.festibed.data.repositories

import fr.uga.miage.m1.festibed.data.entities.HebergementEntity
import fr.uga.miage.m1.festibed.data.entities.NuiteeEntity
import org.springframework.data.domain.Pageable
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param
import java.math.BigDecimal
import java.time.LocalDate
import java.util.UUID

interface HebergementRepository : JpaRepository<HebergementEntity, UUID> {
    fun findAllByEtablissementId(etablissementId: UUID): Collection<HebergementEntity>
    fun findByEtablissementIdAndNumero(etablissementId: UUID, numero: String): HebergementEntity?

    /** Navigation @ManyToMany : hébergements proposant une option (Wi-Fi, parking...). */
    fun findAllByOptionsLibelle(libelle: String): Collection<HebergementEntity>

    /**
     * Hébergements actifs ayant au moins une nuit libre pendant le festival, dans un rectangle
     * géographique autour du festival.
     */
    @Query(
        """select h from HebergementEntity h join h.etablissement e
           where h.actif = true and h.capacite >= :capaciteMin
             and e.latitude between :latMin and :latMax
             and e.longitude between :lonMin and :lonMax
             and exists (select n from NuiteeEntity n where n.hebergement = h and n.selection is null
                         and n.dateNuitee between :debut and :fin)
           order by h.prixNuit""",
    )
    fun rechercherDisponibles(
        @Param("debut") debut: LocalDate,
        @Param("fin") fin: LocalDate,
        @Param("capaciteMin") capaciteMin: Int,
        @Param("latMin") latMin: BigDecimal,
        @Param("latMax") latMax: BigDecimal,
        @Param("lonMin") lonMin: BigDecimal,
        @Param("lonMax") lonMax: BigDecimal,
        page: Pageable,
    ): List<HebergementEntity>
}
