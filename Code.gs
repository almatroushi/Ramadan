// ════════════════════════════════════════════════════════
//  المركز الملكي للمساج — Google Apps Script Backend
//  HOW TO USE:
//  1. Go to: script.google.com → New Project
//  2. Paste this entire file
//  3. Fill in TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID below
//  4. Click Deploy → New Deployment → Web App
//     - Execute as: Me
//     - Who has access: Anyone
//  5. Copy the deployment URL → paste it in index.html and admin.html
//     where it says: YOUR_APPS_SCRIPT_URL_HERE
// ════════════════════════════════════════════════════════

const CONFIG = {
  SHEET_NAME: 'Bookings',
  ADMIN_PASSWORD: 'malaki2025',
  TELEGRAM_BOT_TOKEN: 'YOUR_BOT_TOKEN_HERE',
  TELEGRAM_CHAT_ID:   'YOUR_CHAT_ID_HERE',
};

const SERVICE_NAMES = {
  full_body:     'مساج كامل',
  sports:        'مساج رياضي',
  foot_normatec: 'مساج قدمين — نورماتيك'
};

// ── MAIN ENTRY POINT ──────────────────────────────────
function doGet(e) {
  try {
    const p = e.parameter;
    let result;

    switch (p.action) {
      case 'getSlots':
        result = getSlots(p.date, parseInt(p.duration));
        break;

      case 'book':
        result = createBooking(p, false);
        break;

      case 'admin_getBookings':
        checkAuth(p.password);
        result = getBookings(p.date || null);
        break;

      case 'admin_addBooking':
        checkAuth(p.password);
        result = createBooking(p, true);
        break;

      case 'admin_cancelBooking':
        checkAuth(p.password);
        result = cancelBooking(p.id);
        break;

      default:
        result = { error: 'Unknown action' };
    }

    return respond(result);
  } catch (err) {
    return respond({ error: err.message });
  }
}

// ── AUTH ──────────────────────────────────────────────
function checkAuth(password) {
  if (password !== CONFIG.ADMIN_PASSWORD) throw new Error('Unauthorized');
}

// ── GET SLOTS ─────────────────────────────────────────
function getSlots(date, duration) {
  const sheet = getSheet();
  const rows  = sheet.getDataRange().getValues();
  const occupied = new Set();

  for (let i = 1; i < rows.length; i++) {
    if (rows[i][1] === date && rows[i][7] !== 'cancelled') {
      const start = timeToMin(rows[i][2]);
      const count = Math.ceil(parseInt(rows[i][3]) / 30);
      for (let j = 0; j < count; j++) occupied.add(minToTime(start + j * 30));
    }
  }

  return { bookedSlots: [...occupied] };
}

// ── CREATE BOOKING ────────────────────────────────────
function createBooking(p, isManual) {
  const sheet    = getSheet();
  const duration = parseInt(p.duration);
  const startMin = timeToMin(p.time);
  const count    = Math.ceil(duration / 30);

  // Check for conflicts
  const { bookedSlots } = getSlots(p.date, duration);
  const bookedSet = new Set(bookedSlots);
  for (let i = 0; i < count; i++) {
    if (bookedSet.has(minToTime(startMin + i * 30))) {
      return { error: 'هذا الوقت محجوز — This slot is already booked' };
    }
  }

  const id  = 'BK' + Date.now();
  const now = new Date().toLocaleString('ar-AE', { timeZone: 'Asia/Dubai' });

  sheet.appendRow([
    id, p.date, p.time, duration, p.service,
    p.name, p.phone, 'confirmed', now,
    isManual ? 'manual' : 'online', p.price || 0
  ]);

  sendTelegram(p, id, isManual);
  return { success: true, id };
}

// ── CANCEL BOOKING ────────────────────────────────────
function cancelBooking(id) {
  const sheet = getSheet();
  const rows  = sheet.getDataRange().getValues();

  for (let i = 1; i < rows.length; i++) {
    if (rows[i][0] === id) {
      sheet.getRange(i + 1, 8).setValue('cancelled');
      return { success: true };
    }
  }
  return { error: 'Booking not found' };
}

// ── GET BOOKINGS (ADMIN) ──────────────────────────────
function getBookings(date) {
  const sheet = getSheet();
  const rows  = sheet.getDataRange().getValues();
  const list  = [];

  for (let i = 1; i < rows.length; i++) {
    if (!date || rows[i][1] === date) {
      list.push({
        id:       rows[i][0],
        date:     rows[i][1],
        time:     rows[i][2],
        duration: rows[i][3],
        service:  rows[i][4],
        name:     rows[i][5],
        phone:    rows[i][6],
        status:   rows[i][7],
        created:  rows[i][8],
        isManual: rows[i][9] === 'manual',
        price:    rows[i][10] || 0
      });
    }
  }

  return { bookings: list.filter(b => b.status !== 'cancelled') };
}

// ── TELEGRAM ──────────────────────────────────────────
function sendTelegram(p, id, isManual) {
  if (!CONFIG.TELEGRAM_BOT_TOKEN || CONFIG.TELEGRAM_BOT_TOKEN === 'YOUR_BOT_TOKEN_HERE') return;

  const msg =
    `🔔 *حجز ${isManual ? 'يدوي 📋' : 'جديد 🌐'}*\n` +
    `──────────────\n` +
    `📌 رقم الحجز: \`${id}\`\n` +
    `💆 الخدمة: ${SERVICE_NAMES[p.service] || p.service}\n` +
    `📅 التاريخ: ${p.date}\n` +
    `⏰ الوقت: ${p.time}\n` +
    `⌛ المدة: ${p.duration} دقيقة\n` +
    `💰 السعر: ${p.price || '—'} د.إ\n` +
    `👤 الاسم: ${p.name}\n` +
    `📱 الهاتف: ${p.phone}\n` +
    `──────────────`;

  try {
    UrlFetchApp.fetch(
      `https://api.telegram.org/bot${CONFIG.TELEGRAM_BOT_TOKEN}/sendMessage`,
      {
        method: 'post',
        contentType: 'application/json',
        payload: JSON.stringify({
          chat_id:    CONFIG.TELEGRAM_CHAT_ID,
          text:       msg,
          parse_mode: 'Markdown'
        })
      }
    );
  } catch (e) {
    Logger.log('Telegram error: ' + e.message);
  }
}

// ── HELPERS ───────────────────────────────────────────
function getSheet() {
  const ss    = SpreadsheetApp.getActiveSpreadsheet();
  let   sheet = ss.getSheetByName(CONFIG.SHEET_NAME);

  if (!sheet) {
    sheet = ss.insertSheet(CONFIG.SHEET_NAME);
    sheet.appendRow([
      'ID','Date','Time','Duration','Service',
      'Name','Phone','Status','Created','Type','Price'
    ]);
    sheet.setFrozenRows(1);
    sheet.setColumnWidth(1, 160);
  }
  return sheet;
}

function timeToMin(t) {
  const [h, m] = t.split(':').map(Number);
  return h * 60 + m;
}

function minToTime(m) {
  return `${String(Math.floor(m / 60)).padStart(2,'0')}:${String(m % 60).padStart(2,'0')}`;
}

function respond(data) {
  return ContentService
    .createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}
