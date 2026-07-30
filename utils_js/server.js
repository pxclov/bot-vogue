const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Carregando as configurações compartilhadas
const configPath = path.join(__dirname, '../config.json');
let config = JSON.parse(fs.readFileSync(configPath, 'utf8'));

app.get('/', (req, res) => {
    res.json({
        status: "vogue-utils is running",
        bot_prefix: config.prefix,
        message: "Estrutura base pronta."
    });
});

app.listen(PORT, () => {
    console.log(`rodando ${PORT}`);
});
