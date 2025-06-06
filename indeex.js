const express = require('express');
const cors = require('cors');

const app = express();
const porta = 3000;

app.use(cors({
  origin: 'https://superfsa.intranet.bb.com.br',
  credentials: true
}));

app.get('/api/rels', (req, res) => {
  const { id, prefixo } = req.query;
  if (!prefixo) return res.status(400).json({ erro: 'Prefixo é obrigatório' });

  res.json({
    id,
    prefixo,
    dados: `Simulação de dados para prefixo ${prefixo}`
  });
});

app.listen(porta, () => {
  console.log(`API rodando em http://localhost:${porta}`);
});