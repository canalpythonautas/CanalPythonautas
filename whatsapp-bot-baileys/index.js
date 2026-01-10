const express = require('express')
const { default: makeWASocket, useMultiFileAuthState, DisconnectReason } = require('@whiskeysockets/baileys')
const qrcode = require('qrcode-terminal')

const PORT = 3000

const app = express()
app.use(express.json())

let sock

async function startSock() {
	const {state, saveCreds} = await useMultiFileAuthState('./auth')

	sock = makeWASocket({
		printQRInTerminal: true,
		auth: state
	})

	sock.ev.on('connection.update', (update) => {
		const {connection, lastDisconnect, qr} = update
		if (qr) {
			console.log('\n QR Code:')
			qrcode.generate(qr, {small: true})
		}

		if (connection === 'close') {
			const reason = lastDisconnect?.error?.output?.statusCode
			console.log('Conexão encerrada', reason)
		} else if (connection === 'open') {
			console.log('Whatsapp connectado com sucesso!')
		}

	})

	sock.ev.on('creds.update', saveCreds)

	sock.ev.on('messages.upsert', async ({ messages }) => {
		const msg = messages[0]
		if (!msg.message) return

		const from = msg.key.remoteJid
		const text = msg.message.conversation || msg.message.extendedTextMessage?.text

		console.log('Mensagem recebida de ${from}:', text)

	})

}

app.post('/send_message', async (req, res) => {
	const {number, message} = req.body
	if (!number || !message) {
		return res.status(400).send({error: 'Informe os campos numero e message'})
	}

	try {
		const jid = number.replace(/\D/g, '')+'@s.whatsapp.net'
		await sock.sendMessage(jid,  {text: message})

		res.send({success: true})
	} catch (err) {
		console.error('Erro:', err)
		res.status(500).send({error: 'Erro ao enviar mensagem'})
	}

})

app.listen(PORT, '127.0.0.1', async () => {
	console.log('Servidor iniciando...')
	startSock()
})
