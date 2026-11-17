package com.example.sepet;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.List;

/** Sepet hesabı: kayan nokta hatası olmaması için BigDecimal kullanılır. */
public final class Sepet {

    public static final BigDecimal KDV_ORANI = new BigDecimal("0.20");

    private Sepet() {
    }

    /** Sepetteki bir ürün: fiyat metin olarak verilir ki 0.10 tam olarak 0.10 kalsın. */
    public record Urun(String fiyat, int adet) {
    }

    /** Hesap sonucu: üç tutar da iki ondalık basamaklıdır. */
    public record Sonuc(BigDecimal araToplam, BigDecimal kdv, BigDecimal genelToplam) {
    }

    public static BigDecimal satirToplami(String fiyat, int adet) {
        if (adet <= 0) {
            throw new IllegalArgumentException("adet pozitif bir tam sayi olmali");
        }
        return new BigDecimal(fiyat).multiply(BigDecimal.valueOf(adet));
    }

    public static Sonuc sepetToplami(List<Urun> urunler) {
        BigDecimal araToplam = BigDecimal.ZERO;
        for (Urun urun : urunler) {
            araToplam = araToplam.add(satirToplami(urun.fiyat(), urun.adet()));
        }
        BigDecimal kdv = araToplam.multiply(KDV_ORANI);
        return new Sonuc(yuvarla(araToplam), yuvarla(kdv), yuvarla(araToplam.add(kdv)));
    }

    private static BigDecimal yuvarla(BigDecimal tutar) {
        return tutar.setScale(2, RoundingMode.HALF_UP);
    }
}
