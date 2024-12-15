const express = require('express');
const bodyParser = require('body-parser');
const unluau = require('unluau'); // Biblioteca de decompilação Luau
const crypt = require('crypt'); // Para lidar com base64

const app = express();
const port = 5000;

// Middleware para lidar com requisições JSON
app.use(bodyParser.json());

// Endpoint para decompilar o bytecode
app.post('/unluau/decompile', (req, res) => {
    const { bytecode } = req.body;

    if (!bytecode) {
        return res.status(400).json({ status: 'error', message: 'Bytecode is required' });
    }

    try {
        // Decodifica o bytecode de base64
        const decodedBytecode = crypt.base64.decode(bytecode);
        
        // Decompilando o bytecode usando o unluau
        const decompiledCode = unluau.decompile(decodedBytecode);

        // Enviando o código decompilado de volta
        res.json({ status: 'ok', output: decompiledCode });
    } catch (error) {
        res.status(500).json({ status: 'error', message: 'Decompilation failed', error: error.message });
    }
});

// Iniciar o servidor na porta 3000
app.listen(port, () => {
    console.log(`Servidor de decompilação rodando em http://localhost:${port}`);
});
