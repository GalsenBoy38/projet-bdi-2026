package fr.uga.miage.m1.festibed.repositories

import fr.uga.miage.m1.festibed.data.entities.PaiementEntity
import fr.uga.miage.m1.festibed.data.entities.PassEntity
import fr.uga.miage.m1.festibed.data.entities.ReservationEntity
import fr.uga.miage.m1.festibed.data.entities.SelectionEntity
import fr.uga.miage.m1.festibed.data.repositories.NuiteeRepository
import fr.uga.miage.m1.festibed.data.repositories.PaiementRepository
import fr.uga.miage.m1.festibed.data.repositories.PassRepository
import fr.uga.miage.m1.festibed.data.repositories.ReservationRepository
import fr.uga.miage.m1.festibed.enums.StatutPaiement
import jakarta.persistence.EntityManager
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest
import org.springframework.dao.DataIntegrityViolationException
import org.springframework.test.context.ActiveProfiles
import java.math.BigDecimal
import java.time.LocalDate
import java.time.LocalDateTime
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertNotNull
import kotlin.test.assertNull
import kotlin.test.assertTrue

@DataJpaTest
@ActiveProfiles("test")
class ReservationRepositoryTest {

    @Autowired
    lateinit var reservationRepository: ReservationRepository

    @Autowired
    lateinit var nuiteeRepository: NuiteeRepository

    @Autowired
    lateinit var passRepository: PassRepository

    @Autowired
    lateinit var paiementRepository: PaiementRepository

    @Autowired
    lateinit var em: EntityManager

    private fun reservation(jeu: Jeu, numero: String = "FB0000000001", vararg selections: SelectionEntity) =
        reservationRepository.saveAndFlush(
            ReservationEntity(
                numero = numero, dateReservation = LocalDateTime.of(2027, 3, 1, 10, 0),
                festivalier = jeu.festivalier(), selections = selections.toMutableList(),
            ),
        )

    @Test
    fun `la réservation enregistre ses sélections et leurs Pass en cascade`() {
        val jeu = Jeu(em)
        val festival = jeu.festival()
        val selection = SelectionEntity(
            festival = festival, prixPass = festival.prixPass,
            passes = mutableListOf(PassEntity(code = "PASS-1"), PassEntity(code = "PASS-2")),
        )
        val r = reservation(jeu, "FB0000000001", selection)
        em.clear()

        val relue = reservationRepository.findByNumero("FB0000000001")!!
        assertEquals(1, relue.selections.size)
        assertEquals(setOf("PASS-1", "PASS-2"), relue.selections.first().passes.map { it.code }.toSet())
        assertNotNull(passRepository.findByCode("PASS-2"))

        reservationRepository.delete(relue)
        reservationRepository.flush()
        assertNull(passRepository.findByCode("PASS-2"))
        assertTrue(reservationRepository.findById(r.id!!).isEmpty)
    }

    @Test
    fun `un festival n'apparaît qu'une fois par réservation`() {
        val jeu = Jeu(em)
        val festival = jeu.festival()

        assertFailsWith<DataIntegrityViolationException> {
            reservation(
                jeu, "FB0000000002",
                SelectionEntity(festival = festival, prixPass = festival.prixPass),
                SelectionEntity(festival = festival, prixPass = festival.prixPass),
            )
        }
    }

    @Test
    fun `validation anonyme par numéro et email`() {
        val jeu = Jeu(em)
        reservation(jeu, "FB0000000003")

        assertNotNull(reservationRepository.findByNumeroAndFestivalierEmail("FB0000000003", "camille@festibed.test"))
        assertNull(reservationRepository.findByNumeroAndFestivalierEmail("FB0000000003", "pirate@exemple.com"))
    }

    @Test
    fun `occuper ne prend que les nuits libres`() {
        val jeu = Jeu(em)
        val festival = jeu.festival()
        val h = jeu.hebergement()
        val nuits = jeu.nuits(h, LocalDate.of(2027, 7, 12), 3).map { it.dateNuitee }
        val r1 = reservation(jeu, "FB0000000004", SelectionEntity(festival = festival, prixPass = festival.prixPass))
        val autre = jeu.festival("Autre")
        val r2 = reservationRepository.saveAndFlush(
            ReservationEntity(
                numero = "FB0000000005", dateReservation = LocalDateTime.now(), festivalier = jeu.festivalier("lucas@festibed.test"),
                selections = mutableListOf(SelectionEntity(festival = autre, prixPass = autre.prixPass)),
            ),
        )

        assertEquals(2, nuiteeRepository.occuper(r1.selections.first(), h.id!!, nuits.take(2)))
        assertEquals(1, nuiteeRepository.occuper(r2.selections.first(), h.id!!, nuits))   // seule la 3e nuit était libre
        assertEquals(2, nuiteeRepository.findAllBySelectionId(r1.selections.first().id!!).size)

        val nuitPrise = nuiteeRepository.findAllBySelectionId(r1.selections.first().id!!).first()
        assertEquals(0, nuiteeRepository.retirerSiLibre(nuitPrise.id!!))
        assertEquals(2, nuiteeRepository.liberer(r1.selections.first()))
        assertEquals(1, nuiteeRepository.retirerSiLibre(nuitPrise.id!!))
    }

    @Test
    fun `une nuit d'un hébergement n'existe qu'une fois`() {
        val jeu = Jeu(em)
        val h = jeu.hebergement()
        jeu.nuits(h, LocalDate.of(2027, 7, 12), 1)

        assertFailsWith<Exception> { jeu.nuits(h, LocalDate.of(2027, 7, 12), 1) }
    }

    @Test
    fun `un paiement par réservation, NON_GERE par défaut`() {
        val r = reservation(Jeu(em), "FB0000000006")
        paiementRepository.saveAndFlush(PaiementEntity(reservation = r, montant = BigDecimal("200.00")))

        assertEquals(StatutPaiement.NON_GERE, paiementRepository.findByReservationId(r.id!!)!!.statut)
        assertFailsWith<DataIntegrityViolationException> {
            paiementRepository.saveAndFlush(PaiementEntity(reservation = r, montant = BigDecimal("1.00")))
        }
    }
}
