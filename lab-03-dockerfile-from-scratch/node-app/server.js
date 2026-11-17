const express = require('express');

const app = express();

app.get('/', (req, res) => {
  res.json({ dil: 'nodejs', mesaj: 'Merhaba Docker' });
});

app.listen(3000, '0.0.0.0', () => {
  console.log('Sunucu 3000 portunda calisiyor');
});
