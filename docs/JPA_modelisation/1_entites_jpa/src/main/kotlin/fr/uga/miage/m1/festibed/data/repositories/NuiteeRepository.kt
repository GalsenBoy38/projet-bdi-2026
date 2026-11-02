package fr.uga.miage.m1.festibed.data.repositories

import fr.uga.miage.m1.festibed.data.entities.HebergementId
import fr.uga.miage.m1.festibed.data.entities.NuiteeEntity
import fr.uga.miage.m1.festibed.data.entities.NuiteeId
import fr.uga.miage.m1.festibed.data.entities.SelectionEntity
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Modifying
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param
import java.time.LocalDate

interface NuiteeRepository : JpaRepository<NuiteeEntity, NuiteeId> {
    fun findAllBySelectionId(selectionId: Long): Collection<NuiteeEntity>

    /**
     * Occupe les nuits d'un hébergement pour une sélection, seulement si elles sont encore libres.
     * Succès si la valeur renvoyée == nuits.size ; sinon une autre validation a pris une nuit => rollback.
     */
    @Modifying(clearAutomatically = true, flushAutomatically = true)
    @Query(
        """update NuiteeEntity n set n.selection = :selection
           where n.id.hebergementId = :hebergement and n.id.dateNuitee in :nuits and n.selection is null""",
    )
    fun occuper(
        @Param("selection") selection: SelectionEntity,
        @Param("hebergement") hebergement: HebergementId,
        @Param("nuits") nuits: Collection<LocalDate>,
    ): Int

    /** Annulation (désactivation d'un festival) : les nuitées redeviennent libres. */
    @Modifying(clearAutomatically = true, flushAutomatically = true)
    @Query("update NuiteeEntity n set n.selection = null where n.selection = :selection")
    fun liberer(@Param("selection") selection: SelectionEntity): Int

    /** L'hébergeur retire une nuit : impossible si elle est déjà réservée (règle « Modification de l'offre »). */
    @Modifying(clearAutomatically = true, flushAutomatically = true)
    @Query("delete from NuiteeEntity n where n.id = :id and n.selection is null")
    fun retirerSiLibre(@Param("id") id: NuiteeId): Int

    @Query(
        """select n from NuiteeEntity n
           where n.hebergement.id = :h and n.selection is null and n.id.dateNuitee between :debut and :fin
           order by n.id.dateNuitee""",
    )
    fun nuitsLibres(
        @Param("h") hebergement: HebergementId,
        @Param("debut") debut: LocalDate,
        @Param("fin") fin: LocalDate,
    ): List<NuiteeEntity>
}
