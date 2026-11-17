"""Sepet hesabı: kayan nokta hatası olmaması için Decimal kullanılır."""
import json
from decimal import Decimal, ROUND_HALF_UP

from babel.numbers import format_currency

KDV_ORANI = Decimal("0.20")
KURUS = Decimal("0.01")


def satir_toplami(fiyat, adet):
    if not isinstance(adet, int) or adet <= 0:
        raise ValueError("adet pozitif bir tam sayi olmali")
    return Decimal(fiyat) * adet


def sepet_toplami(urunler):
    ara_toplam = sum((satir_toplami(u["fiyat"], u["adet"]) for u in urunler), Decimal("0"))
    kdv = ara_toplam * KDV_ORANI
    return {
        "ara_toplam": ara_toplam.quantize(KURUS, ROUND_HALF_UP),
        "kdv": kdv.quantize(KURUS, ROUND_HALF_UP),
        "genel_toplam": (ara_toplam + kdv).quantize(KURUS, ROUND_HALF_UP),
    }


def tl_formatla(tutar):
    return format_currency(tutar, "TRY", locale="tr_TR")


# Örnek sepetin toplamını hesaplar ve sonucu JSON olarak ekrana yazar.
# Build'den sonra uygulamanın gerçekten çalıştığını görmek için.
ORNEK_SEPET = [
    {"fiyat": "100.00", "adet": 2},
    {"fiyat": "0.10", "adet": 1},
    {"fiyat": "0.20", "adet": 1},
]


if __name__ == "__main__":
    sonuc = sepet_toplami(ORNEK_SEPET)
    print(json.dumps({
        "araToplam": str(sonuc["ara_toplam"]),
        "kdv": str(sonuc["kdv"]),
        "genelToplam": str(sonuc["genel_toplam"]),
    }, separators=(",", ":")))
