package com.example.sepet;

import java.util.List;

/**
 * Örnek sepetin toplamını hesaplar ve sonucu JSON olarak ekrana yazar.
 * Build'den sonra uygulamanın gerçekten çalıştığını görmek için.
 */
public final class App {

    static final List<Sepet.Urun> ORNEK_SEPET = List.of(
            new Sepet.Urun("100.00", 2),
            new Sepet.Urun("0.10", 1),
            new Sepet.Urun("0.20", 1));

    private App() {
    }

    static String json(Sepet.Sonuc sonuc) {
        return "{\"araToplam\":\"" + sonuc.araToplam()
                + "\",\"kdv\":\"" + sonuc.kdv()
                + "\",\"genelToplam\":\"" + sonuc.genelToplam() + "\"}";
    }

    public static void main(String[] args) {
        System.out.println(json(Sepet.sepetToplami(ORNEK_SEPET)));
    }
}
