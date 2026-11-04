package fr.uga.miage.m1.festibed.data.entities

import fr.uga.miage.m1.festibed.enums.Domaine
import fr.uga.miage.m1.festibed.enums.Periodicite
import fr.uga.miage.m1.festibed.enums.SousDomaine
import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.EnumType
import jakarta.persistence.Enumerated
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.Index
import jakarta.persistence.JoinColumn
import jakarta.persistence.ManyToOne
import jakarta.persistence.Table
import org.hibernate.annotations.ColumnDefault
import java.math.BigDecimal
import java.time.LocalDate
import java.util.UUID

@Entity
@Table(
    name = "festival",
    indexes = [
        Index(name = "idx_festival_dates", columnList = "date_debut, date_fin"),
        Index(name = "idx_festival_domaine", columnList = "domaine"),
    ],
)
data class FestivalEntity(
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(nullable = false)
    val id: UUID? = null,

    @Column(nullable = false, length = 100)
    var nom: String,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 40)
    var domaine: Domaine,

    @Enumerated(EnumType.STRING)
    @Column(name = "sous_domaine", length = 40)
    var sousDomaine: SousDomaine? = null,

    @Enumerated(EnumType.STRING)
    @Column(length = 30)
    var periodicite: Periodicite? = null,

    @Column(name = "site_web", length = 150)
    var siteWeb: String? = null,

    @Column(name = "date_creation")
    var dateCreation: LocalDate? = null,

    @Column(name = "code_postal", nullable = false, length = 5)
    var codePostal: String,

    @Column(name = "date_debut", nullable = false)
    var dateDebut: LocalDate,

    @Column(name = "date_fin", nullable = false)
    var dateFin: LocalDate,

    /** Nombre maximal de Pass confiés à FestiBed (>= 30). */
    @Column(name = "quota_pass", nullable = false)
    var quotaPass: Int,

    @Column(name = "prix_pass", nullable = false, precision = 8, scale = 2)
    var prixPass: BigDecimal,

    /**
     * Pass déjà vendus. LECTURE SEULE pour JPA : modifié uniquement par l'UPDATE conditionnel
     * FestivalRepository.reserverPass ; sinon la sauvegarde d'un festival modifié par l'organisateur
     * écraserait les ventes faites entre-temps (stratégie de concurrence).
     */
    @ColumnDefault("0")
    @Column(name = "nb_pass_vendus", nullable = false, insertable = false, updatable = false)
    val nbPassVendus: Int = 0,

    @Column(nullable = false)
    var actif: Boolean = true,

    @ManyToOne(optional = false)
    @JoinColumn(name = "commune_id", nullable = false)
    var commune: CommuneEntity,

    @ManyToOne
    @JoinColumn(name = "organisateur_id")
    var organisateur: OrganisateurEntity? = null,
) {

    val passDisponibles: Int get() = quotaPass - nbPassVendus
}
