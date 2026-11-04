package fr.uga.miage.m1.festibed.data.repositories

import fr.uga.miage.m1.festibed.data.entities.NuiteeEntity
import fr.uga.miage.m1.festibed.data.entities.SelectionEntity
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Modifying
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param
import java.time.LocalDate
import java.util.UUID

interface NuiteeRepository : JpaRepository<NuiteeEntity, UUID> {
    fun findAllBySelectionId(selectionId: UUID): Collection<NuiteeEntity>
    fun findAllByHebergementIdAndSelectionIsNullAndDateNuiteeBetweenOrderByDateNuitee(
        hebergementId: UUID,
        debut: LocalDate,
        fin: LocalDate,
    ): List<NuiteeEntity>

    /**
     * Occupe des nuits d'un hébergement pour une sélection, seulement si elles sont encore libres.
     * Succès si la valeur renvoyée == nuits.size ; sinon une autre validation a pris une nuit => rollback.
     */
    @Modifying(clearAutomatically = true, flushAutomatically = true)
    @Query(
        """update NuiteeEntity n set n.selection = :selection
           where n.hebergement.id = :hebergementId and n.dateNuitee in :nuits and n.selection is null""",
    )
    fun occuper(
        @Param("selection") selection: SelectionEntity,
        @Param("hebergementId") hebergementId: UUID,
        @Param("nuits") nuits: Collection<LocalDate>,
    ): Int

    /** Annulation (désactivation d'un festival) : les nuitées redeviennent libres. */
    @Modifying(clearAutomatically = true, flushAutomatically = true)
    @Query("update NuiteeEntity n set n.selection = null where n.selection = :selection")
    fun liberer(@Param("selection") selection: SelectionEntity): Int

    /** L'hébergeur retire une nuit : impossible si elle est déjà réservée (règle « Modification de l'offre »). */
    @Modifying(clearAutomatically = true, flushAutomatically = true)
    @Query("delete from NuiteeEntity n where n.id = :id and n.selection is null")
    fun retirerSiLibre(@Param("id") nuiteeId: UUID): Int
}
