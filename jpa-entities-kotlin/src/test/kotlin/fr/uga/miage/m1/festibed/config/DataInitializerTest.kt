package fr.uga.miage.m1.festibed.config

import fr.uga.miage.m1.festibed.data.entities.CampingEntity
import fr.uga.miage.m1.festibed.data.entities.EtablissementNonClasseEntity
import fr.uga.miage.m1.festibed.data.entities.HotelDeTourismeEntity
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
import jakarta.persistence.EntityManager
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.DefaultApplicationArguments
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest
import org.springframework.test.context.ActiveProfiles
import java.math.BigDecimal
import kotlin.test.assertEquals
import kotlin.test.assertIs
import kotlin.test.assertNotNull

@DataJpaTest
@ActiveProfiles("test")
class DataInitializerTest {

    @Autowired lateinit var regionRepository: RegionRepository
    @Autowired lateinit var departementRepository: DepartementRepository
    @Autowired lateinit var communeRepository: CommuneRepository
    @Autowired lateinit var organisateurRepository: OrganisateurRepository
    @Autowired lateinit var hebergeurRepository: HebergeurRepository
    @Autowired lateinit var festivalierRepository: FestivalierRepository
    @Autowired lateinit var festivalRepository: FestivalRepository
    @Autowired lateinit var etablissementRepository: EtablissementRepository
    @Autowired lateinit var optionHebergementRepository: OptionHebergementRepository
    @Autowired lateinit var hebergementRepository: HebergementRepository
    @Autowired lateinit var nuiteeRepository: NuiteeRepository
    @Autowired lateinit var reservationRepository: ReservationRepository
    @Autowired lateinit var paiementRepository: PaiementRepository
    @Autowired lateinit var notationFestivalRepository: NotationFestivalRepository
    @Autowired lateinit var notationEtablissementRepository: NotationEtablissementRepository
    @Autowired lateinit var em: EntityManager

    private lateinit var initializer: DataInitializer

    @BeforeEach
    fun init() {
        initializer = DataInitializer(
            regionRepository, departementRepository, communeRepository, organisateurRepository, hebergeurRepository,
            festivalierRepository, festivalRepository, etablissementRepository, optionHebergementRepository,
            hebergementRepository, nuiteeRepository, reservationRepository, paiementRepository,
            notationFestivalRepository, notationEtablissementRepository,
        )
        initializer.run(DefaultApplicationArguments())
        em.flush()
        em.clear()
    }

    @Test
    fun `les données des scénarios sont créées`() {
        assertEquals(3, festivalRepository.count())
        assertEquals(4, communeRepository.count())
        assertEquals(5, hebergementRepository.count())
        assertEquals(3 * 7 + 2 * 13, nuiteeRepository.count().toInt())
        assertNotNull(organisateurRepository.findByEmail("ronald.organisateur@festibed.test"))
        assertEquals(2, festivalRepository.findAllByOrganisateurId(organisateurRepository.findByEmail("ronald.organisateur@festibed.test")!!.id!!).size)
    }

    @Test
    fun `chaque établissement a sa typologie`() {
        val parNom = etablissementRepository.findAll().associateBy { it.nomCommercial }
        assertIs<CampingEntity>(parNom.getValue("CAMPING INTERNATIONAL DU SIERROZ"))
        assertIs<HotelDeTourismeEntity>(parNom.getValue("HÔTEL DES ARCADES"))
        assertIs<EtablissementNonClasseEntity>(parNom.getValue("Auberge de Jeunesse"))
        assertEquals(0, BigDecimal("4.00").compareTo(parNom.getValue("HÔTEL DES ARCADES").noteMoyenne))
    }

    @Test
    fun `la réservation de démonstration est cohérente`() {
        val reservation = reservationRepository.findByNumeroAndFestivalierEmail("FB7K2M9QX4TA", "camille.martin@festibed.test")!!
        val selection = reservation.selections.single()

        assertEquals("Musilac", selection.festival.nom)
        assertEquals(2, selection.passes.size)
        assertEquals(2, selection.festival.nbPassVendus)
        assertEquals(3, nuiteeRepository.findAllBySelectionId(selection.id!!).size)
        assertEquals(0, BigDecimal("531.00").compareTo(paiementRepository.findByReservationId(reservation.id!!)!!.montant))
    }

    @Test
    fun `les options sont reliées aux hébergements`() {
        assertEquals(5, hebergementRepository.findAllByOptionsLibelle("Wi-Fi").size)
        assertEquals("H002", hebergementRepository.findAllByOptionsLibelle("Piscine").single().numero)
    }

    @Test
    fun `une seconde exécution ne duplique rien`() {
        initializer.run(DefaultApplicationArguments())

        assertEquals(3, festivalRepository.count())
    }
}
