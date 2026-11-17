package com.example.sepet;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.math.BigDecimal;
import java.util.List;
import org.junit.jupiter.api.Test;

class SepetTest {

    @Test
    void ondalikliFiyatlarKayanNoktaHatasiOlmadanToplanir() {
        Sepet.Sonuc sonuc = Sepet.sepetToplami(List.of(
                new Sepet.Urun("0.10", 1),
                new Sepet.Urun("0.20", 1)));
        assertEquals(new BigDecimal("0.30"), sonuc.araToplam());
    }

    @Test
    void kdvYuzde20OlarakHesaplanir() {
        Sepet.Sonuc sonuc = Sepet.sepetToplami(List.of(new Sepet.Urun("100.00", 2)));
        assertEquals(new BigDecimal("40.00"), sonuc.kdv());
        assertEquals(new BigDecimal("240.00"), sonuc.genelToplam());
    }

    @Test
    void bosSepetinToplamiSifirdir() {
        Sepet.Sonuc sonuc = Sepet.sepetToplami(List.of());
        assertEquals(new BigDecimal("0.00"), sonuc.genelToplam());
    }

    @Test
    void gecersizAdetHataVerir() {
        assertThrows(IllegalArgumentException.class, () -> Sepet.satirToplami("10.00", 0));
    }
}
