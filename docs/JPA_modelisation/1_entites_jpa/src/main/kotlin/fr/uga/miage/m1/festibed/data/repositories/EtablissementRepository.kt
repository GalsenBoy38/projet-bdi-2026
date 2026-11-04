package fr.uga.miage.m1.festibed.data.repositories

import fr.uga.miage.m1.festibed.data.entities.EtablissementEntity
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Modifying
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param
import java.math.BigDecimal
import java.util.UUID

interface EtablissementRepository : JpaRepository<EtablissementEntity, UUID> {
    fun findAllByHebergeurId(hebergeurId: UUID): Collection<EtablissementEntity>

    /** Nouvelle note : moyenne et compteur mis à jour en une instruction (pas de perte en concurrence). */
    @Modifying(clearAutomatically = true, flushAutomatically = true)
    @Query(
        """update EtablissementEntity e set
             e.noteMoyenne = (coalesce(e.noteMoyenne, 0) * e.nbNotes + :note) / (e.nbNotes + 1),
             e.nbNotes = e.nbNotes + 1
           where e.id = :id""",
    )
    fun ajouterNote(@Param("id") idEtablissement: UUID, @Param("note") note: BigDecimal): Int
}
