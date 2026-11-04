package fr.uga.miage.m1.festibed.data.repositories

import fr.uga.miage.m1.festibed.data.entities.FestivalEntity
import fr.uga.miage.m1.festibed.enums.Domaine
import org.springframework.data.domain.Pageable
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Modifying
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param
import java.math.BigDecimal
import java.time.LocalDate
import java.util.UUID

/*
 * Règle de concurrence (stratégie du 23/10) : les ressources disputées (Pass d'un festival, nuitées)
 * ne sont JAMAIS modifiées par « lecture puis save() ». On utilise un UPDATE conditionnel : la condition
 * et l'écriture sont atomiques, et le nombre de lignes modifiées dit si c'est réussi.
 * À appeler dans une transaction (@Transactional de l'adapter / du service de validation).
 */
interface FestivalRepository : JpaRepository<FestivalEntity, UUID> {
    fun findAllByOrganisateurId(organisateurId: UUID): Collection<FestivalEntity>

    /** Réserve n Pass. Renvoie 1 si c'est fait, 0 s'il n'en reste pas assez (=> rollback de la validation). */
    @Modifying(clearAutomatically = true, flushAutomatically = true)
    @Query(
        """update FestivalEntity f set f.nbPassVendus = f.nbPassVendus + :n
           where f.id = :id and f.actifFestival = true and f.nbPassVendus + :n <= f.quotaPass""",
    )
    fun reserverPass(@Param("id") idFestival: UUID, @Param("n") nbPass: Int): Int

    /** Libère n Pass (annulation). */
    @Modifying(clearAutomatically = true, flushAutomatically = true)
    @Query("update FestivalEntity f set f.nbPassVendus = f.nbPassVendus - :n where f.id = :id and f.nbPassVendus >= :n")
    fun libererPass(@Param("id") idFestival: UUID, @Param("n") nbPass: Int): Int

    /** L'organisateur change son quota : refusé (0) s'il descend sous les Pass déjà vendus ou sous 30. */
    @Modifying(clearAutomatically = true, flushAutomatically = true)
    @Query("update FestivalEntity f set f.quotaPass = :q where f.id = :id and :q >= f.nbPassVendus and :q >= 30")
    fun modifierQuota(@Param("id") idFestival: UUID, @Param("q") quota: Int): Int

    /** Recherche du festivalier : seulement les festivals actifs ayant encore des Pass. */
    @Query(
        """select f from FestivalEntity f join fetch f.commune c
           where f.actifFestival = true and f.nbPassVendus < f.quotaPass
             and f.dateFinFestival >= :debut and f.dateDebutFestival <= :fin
             and (:domaine is null or f.domaine = :domaine)
             and (:prixMax is null or f.prixPass <= :prixMax)
           order by f.dateDebutFestival""",
    )
    fun rechercher(
        @Param("debut") debut: LocalDate,
        @Param("fin") fin: LocalDate,
        @Param("domaine") domaine: Domaine?,
        @Param("prixMax") prixMax: BigDecimal?,
        page: Pageable,
    ): List<FestivalEntity>
}
