// Örnek sepetin toplamını hesaplar ve sonucu JSON olarak ekrana yazar.
// Build'den sonra uygulamanın gerçekten çalıştığını görmek için.
const { sepetToplami } = require('./cart');

const ORNEK_SEPET = [
  { fiyat: '100.00', adet: 2 },
  { fiyat: '0.10', adet: 1 },
  { fiyat: '0.20', adet: 1 },
];

console.log(JSON.stringify(sepetToplami(ORNEK_SEPET)));
