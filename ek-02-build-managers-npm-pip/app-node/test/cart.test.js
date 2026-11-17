const test = require('node:test');
const assert = require('node:assert/strict');
const { satirToplami, sepetToplami } = require('../src/cart');

test('ondalikli fiyatlar kayan nokta hatasi olmadan toplanir', () => {
  const sonuc = sepetToplami([
    { fiyat: '0.10', adet: 1 },
    { fiyat: '0.20', adet: 1 },
  ]);
  assert.equal(sonuc.araToplam, '0.30');
});

test('KDV yuzde 20 olarak hesaplanir', () => {
  const sonuc = sepetToplami([{ fiyat: '100.00', adet: 2 }]);
  assert.equal(sonuc.kdv, '40.00');
  assert.equal(sonuc.genelToplam, '240.00');
});

test('bos sepetin toplami sifirdir', () => {
  assert.deepEqual(sepetToplami([]), { araToplam: '0.00', kdv: '0.00', genelToplam: '0.00' });
});

test('gecersiz adet hata verir', () => {
  assert.throws(() => satirToplami('10.00', 0), /pozitif/);
});
