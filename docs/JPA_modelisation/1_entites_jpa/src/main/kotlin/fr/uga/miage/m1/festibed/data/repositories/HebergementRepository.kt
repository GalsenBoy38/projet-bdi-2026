package fr.uga.miage.m1.festibed.data.repositories

import fr.uga.miage.m1.festibed.data.entities.HebergementEntity
import fr.uga.miage.m1.festibed.data.entities.HebergementId
import org.springframework.data.domain.Pageable
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param
import java.math.BigDecimal
import java.time.LocalDate

interface HebergementRepository : JpaRepository<HebergementEntity, HebergementId> {
    fun findAllByEtablissementId(etablissementId: Long): Collection<HebergementEntity>

    /**
     * Hébergements actifs ayant au moins une nuit libre pendant le festival, dans un rectangle
     * géographique autour du festival (index IX_ETABLISSEMENT_1 latitude/longitude).
     */
    @Query(
        """select new fr.uga.miage.m1.festibed.data.repositories.HebergementDisponible(
               e.id, h.id.numeroHebergement, e.nomCommercial, e.nomCommuneEtablissement,
               cast(h.typeHebergement as string), h.capaciteHebergement, h.prixNuitHebergement, e.noteMoyenne,
               e.latitudeEtablissement, e.longitudeEtablissement)
           from HebergementEntity h join h.etablissement e
           where h.actifHebergement = true and h.capaciteHebergement >= :capaciteMin
             and e.latitudeEtablissement between :latMin and :latMax
             and e.longitudeEtablissement between :lonMin and :lonMax
             and exists (select 1 from NuiteeEntity n where n.hebergement = h and n.selection is null
                         and n.id.dateNuitee between :debut and :fin)
           order by h.prixNuitHebergement""",
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
    ): List<HebergementDisponible>
}
