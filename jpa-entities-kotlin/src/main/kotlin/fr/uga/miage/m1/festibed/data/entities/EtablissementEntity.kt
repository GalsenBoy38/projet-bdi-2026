package fr.uga.miage.m1.festibed.data.entities

import fr.uga.miage.m1.festibed.enums.Classement
import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.EnumType
import jakarta.persistence.Enumerated
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.Index
import jakarta.persistence.Inheritance
import jakarta.persistence.InheritanceType
import jakarta.persistence.JoinColumn
import jakarta.persistence.ManyToOne
import jakarta.persistence.Table
import jakarta.persistence.UniqueConstraint
import org.hibernate.annotations.ColumnDefault
import java.math.BigDecimal
import java.time.LocalDate
import java.util.UUID

/**
 * Établissement d'hébergement. Héritage JOINED : une table par typologie
 * (6 typologies classées + EtablissementNonClasseEntity issu d'OpenStreetMap).
 * Classe abstraite et non data class : Kotlin interdit d'hériter d'une data class.
 */
@Entity
@Table(
    name = "etablissement",
    uniqueConstraints = [UniqueConstraint(name = "uk_etablissement_osm_ref", columnNames = ["osm_ref"])],
    indexes = [
        Index(name = "idx_etablissement_position", columnList = "latitude, longitude"),
        Index(name = "idx_etablissement_code_postal", columnList = "code_postal"),
    ],
)
@Inheritance(strategy = InheritanceType.JOINED)
abstract class EtablissementEntity(
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(nullable = false)
    val id: UUID? = null,

    @Column(name = "nom_commercial", nullable = false, length = 100)
    var nomCommercial: String,

    @Column(length = 80)
    var adresse: String? = null,

    @Column(name = "code_postal", nullable = false, length = 5)
    var codePostal: String,

    /** Libellé postal ; la commune INSEE est dans « commune ». */
    @Column(name = "nom_commune", nullable = false, length = 60)
    var nomCommune: String,

    @ManyToOne
    @JoinColumn(name = "commune_id")
    var commune: CommuneEntity? = null,

    @Column(length = 30)
    var telephone: String? = null,

    @Column(length = 150)
    var email: String? = null,

    @Column(name = "site_web", length = 350)
    var siteWeb: String? = null,

    @Column(name = "capacite_accueil", nullable = false)
    var capaciteAccueil: Int,

    /** classement, dateClassement, classementProroge : renseignés pour un établissement classé, null sinon. */
    @Enumerated(EnumType.STRING)
    @Column(length = 30)
    var classement: Classement? = null,

    @Column(name = "date_classement")
    var dateClassement: LocalDate? = null,

    @Column(name = "classement_proroge")
    var classementProroge: Boolean? = null,

    @Column(precision = 12, scale = 9)
    var latitude: BigDecimal? = null,

    @Column(precision = 12, scale = 9)
    var longitude: BigDecimal? = null,

    /** Objet OpenStreetMap correspondant (« node/123 »). */
    @Column(name = "osm_ref", length = 25)
    var osmRef: String? = null,

    @ManyToOne
    @JoinColumn(name = "hebergeur_id")
    var hebergeur: HebergeurEntity? = null,
) {
    /**
     * Moyenne des notes, dénormalisée pour le filtre « note de l'établissement ».
     * LECTURE SEULE pour JPA : mise à jour par EtablissementRepository.ajouterNote (UPDATE atomique).
     */
    @Column(name = "note_moyenne", precision = 3, scale = 2, insertable = false, updatable = false)
    val noteMoyenne: BigDecimal? = null

    @ColumnDefault("0")
    @Column(name = "nb_notes", nullable = false, insertable = false, updatable = false)
    val nbNotes: Int = 0

    val estClasse: Boolean get() = classement != null

    override fun equals(other: Any?) = this === other || (other is EtablissementEntity && id != null && id == other.id)
    override fun hashCode() = EtablissementEntity::class.hashCode()
    override fun toString() = "${this::class.simpleName}(id=$id, nomCommercial=$nomCommercial)"
}
