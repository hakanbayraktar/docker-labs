// Sepet hesabı: kayan nokta hatası olmaması için Decimal kullanılır (0.1 + 0.2 = 0.3)
const Decimal = require('decimal.js');

const KDV_ORANI = new Decimal('0.20');

function satirToplami(fiyat, adet) {
  if (!Number.isInteger(adet) || adet <= 0) {
    throw new Error('adet pozitif bir tam sayi olmali');
  }
  return new Decimal(fiyat).times(adet);
}

function sepetToplami(urunler) {
  const araToplam = urunler.reduce(
    (toplam, urun) => toplam.plus(satirToplami(urun.fiyat, urun.adet)),
    new Decimal(0),
  );
  const kdv = araToplam.times(KDV_ORANI);
  return {
    araToplam: araToplam.toFixed(2),
    kdv: kdv.toFixed(2),
    genelToplam: araToplam.plus(kdv).toFixed(2),
  };
}

module.exports = { satirToplami, sepetToplami, KDV_ORANI };
