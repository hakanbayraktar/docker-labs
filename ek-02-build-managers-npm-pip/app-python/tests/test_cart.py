from decimal import Decimal

import pytest

from cart import satir_toplami, sepet_toplami, tl_formatla


def test_ondalikli_fiyatlar_kayan_nokta_hatasi_olmadan_toplanir():
    sonuc = sepet_toplami([{"fiyat": "0.10", "adet": 1}, {"fiyat": "0.20", "adet": 1}])
    assert sonuc["ara_toplam"] == Decimal("0.30")


def test_kdv_yuzde_20_olarak_hesaplanir():
    sonuc = sepet_toplami([{"fiyat": "100.00", "adet": 2}])
    assert sonuc["kdv"] == Decimal("40.00")
    assert sonuc["genel_toplam"] == Decimal("240.00")


def test_gecersiz_adet_hata_verir():
    with pytest.raises(ValueError):
        satir_toplami("10.00", 0)


def test_tutar_turk_lirasi_bicimiyle_gosterilir():
    assert tl_formatla(Decimal("1234.50")) == "₺1.234,50"
