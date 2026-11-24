/**
 * WhatsApp Web bridge.
 *
 * Opens WhatsApp Web in a Chrome window on your computer and links it to your normal WhatsApp
 * number (scan the QR code once from your phone: Settings > Linked devices). Then it:
 *   - forwards every private chat message to the Python agent (POST {AGENT_URL}/bridge/inbound)
 *   - exposes a small local API the agent uses to send messages and read the connection status.
 *
 * The API listens on 127.0.0.1 only, so nothing outside your computer can use it.
 */

const express = require('express');
const QRCode = require('qrcode');
const { Client, LocalAuth } = require('whatsapp-web.js');

const PORT = Number(process.env.BRIDGE_PORT || 3100);
const AGENT_URL = process.env.AGENT_URL || 'http://127.0.0.1:8000';
const SECRET = process.env.BRIDGE_SECRET || '';
const HEADLESS = (process.env.BRIDGE_HEADLESS || 'false').toLowerCase() === 'true';
const CHROME_PATH = process.env.CHROME_PATH || undefined;
const SESSION_DIR = process.env.BRIDGE_SESSION_DIR || './.wwebjs_auth';

const state = { status: 'starting', qr: null, me: null, lastError: null, since: new Date().toISOString() };

// Messages the agent asked us to send. Their "message_create" echo must not be mistaken for a
// message you typed yourself on the phone (which pauses the agent for that lead).
const pendingSends = new Map();
const pendingKey = (chatId, text) => `${chatId}|${(text || '').trim()}`;

const client = new Client({
  authStrategy: new LocalAuth({ dataPath: SESSION_DIR }),
  puppeteer: {
    headless: HEADLESS,
    executablePath: CHROME_PATH,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  },
});

function log(...args) {
  console.log(new Date().toISOString(), '[bridge]', ...args);
}

async function postToAgent(payload) {
  try {
    const res = await fetch(`${AGENT_URL}/bridge/inbound`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Bridge-Secret': SECRET },
      body: JSON.stringify(payload),
    });
    if (!res.ok) log('agent rejected message:', res.status, await res.text());
  } catch (err) {
    log('could not reach the agent at', AGENT_URL, '-', err.message);
  }
}

/** Turn a chat id (2010...@c.us or ...@lid) into plain international digits. */
async function phoneFromChatId(chatId) {
  if (chatId.endsWith('@c.us')) return chatId.split('@')[0];
  if (chatId.endsWith('@lid')) {
    try {
      const [pair] = await client.getContactLidAndPhone([chatId]);
      if (pair && pair.pn) return pair.pn.split('@')[0];
    } catch (err) {
      log('lid lookup failed for', chatId, err.message);
    }
    try {
      const contact = await client.getContactById(chatId);
      if (contact && contact.number) return contact.number;
    } catch (_) { /* ignore */ }
  }
  return null;
}

const MEDIA_LABELS = {
  ptt: '[sent a voice note]', audio: '[sent an audio file]', image: '[sent an image]', video: '[sent a video]',
  document: '[sent a file]', sticker: '[sent a sticker]', location: '[shared a location]', vcard: '[shared a contact]',
};

client.on('qr', async (qr) => {
  state.status = 'qr';
  state.qr = await QRCode.toDataURL(qr);
  log('scan the QR code (shown in the dashboard and the browser window)');
});
client.on('authenticated', () => { state.status = 'authenticated'; state.qr = null; log('authenticated'); });
client.on('auth_failure', (msg) => { state.status = 'auth_failure'; state.lastError = msg; log('auth failure', msg); });
client.on('ready', () => {
  state.status = 'ready';
  state.qr = null;
  state.me = client.info && client.info.wid ? client.info.wid.user : null;
  state.since = new Date().toISOString();
  log('WhatsApp is ready as', state.me);
});
client.on('disconnected', (reason) => {
  state.status = 'disconnected';
  state.lastError = String(reason);
  log('disconnected:', reason, '- restarting in 10s');
  setTimeout(() => client.initialize().catch((e) => log('re-init failed', e.message)), 10000);
});

// Fires for every new message: incoming ones and ones sent from this number (phone, desktop app or API).
client.on('message_create', async (msg) => {
  try {
    if (msg.isStatus || msg.broadcast) return;
    const chatId = msg.fromMe ? msg.to : msg.from;
    if (!chatId || chatId.endsWith('@g.us') || chatId.endsWith('@newsletter') || chatId === 'status@broadcast') return;

    if (msg.fromMe) {
      const key = pendingKey(chatId, msg.body);
      if (pendingSends.has(key)) {
        const left = pendingSends.get(key) - 1;
        if (left <= 0) pendingSends.delete(key); else pendingSends.set(key, left);
        return; // the agent sent this one itself
      }
    }

    const phone = await phoneFromChatId(chatId);
    if (!phone) return;
    let profileName = '';
    if (!msg.fromMe) {
      try { profileName = (await msg.getContact()).pushname || ''; } catch (_) { /* ignore */ }
    }
    const text = msg.type === 'chat' ? msg.body : `${MEDIA_LABELS[msg.type] || `[sent a ${msg.type} message]`}${msg.body ? ` caption: ${msg.body}` : ''}`;
    await postToAgent({
      phone,
      wa_message_id: msg.id && msg.id._serialized,
      profile_name: profileName,
      type: msg.type === 'chat' ? 'text' : msg.type,
      text,
      from_me: msg.fromMe,
    });
  } catch (err) {
    log('error handling message', err.message);
  }
});

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const app = express();
app.use(express.json({ limit: '1mb' }));
app.use((req, res, next) => {
  if (SECRET && req.get('X-Bridge-Secret') !== SECRET) return res.status(401).json({ error: 'bad secret' });
  next();
});

app.get('/status', (req, res) => res.json(state));

app.post('/send', async (req, res) => {
  const { phone, text } = req.body || {};
  if (!phone || !text) return res.status(400).json({ error: 'phone and text are required' });
  if (state.status !== 'ready') return res.status(503).json({ error: `WhatsApp is not connected (status: ${state.status})` });
  try {
    const numberId = await client.getNumberId(String(phone).replace(/\D/g, ''));
    if (!numberId) return res.status(404).json({ error: 'not_on_whatsapp' });
    const chatId = numberId._serialized;
    // Show "typing..." for a moment, roughly like a person would.
    try {
      const chat = await client.getChatById(chatId);
      await chat.sendStateTyping();
      await sleep(Math.min(6000, 800 + text.length * 40));
    } catch (_) { /* chat may not exist yet - fine */ }
    const key = pendingKey(chatId, text);
    pendingSends.set(key, (pendingSends.get(key) || 0) + 1);
    setTimeout(() => pendingSends.delete(key), 120000);
    const sent = await client.sendMessage(chatId, text);
    res.json({ id: sent && sent.id ? sent.id._serialized : null });
  } catch (err) {
    log('send failed', err.message);
    res.status(500).json({ error: err.message });
  }
});

app.post('/logout', async (req, res) => {
  try { await client.logout(); } catch (err) { return res.status(500).json({ error: err.message }); }
  state.status = 'logged_out';
  res.json({ ok: true });
  setTimeout(() => client.initialize().catch((e) => log('re-init failed', e.message)), 2000);
});

app.listen(PORT, '127.0.0.1', () => log(`bridge API on http://127.0.0.1:${PORT}, forwarding to ${AGENT_URL}`));
log('starting WhatsApp Web...');
client.initialize().catch((err) => {
  state.status = 'error';
  state.lastError = err.message;
  log('failed to start WhatsApp Web:', err.message);
});
