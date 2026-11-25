// Generador de firma de correo institucional (Apps Script, aplicación web).
// Formato: Manual de identidad 2.18 (Verdana, tamaños) + color #0077C8 de la Guía de marca 2022.

// URL pública del logo.
const LOGO_URL = 'PEGA_AQUI_LA_URL_DEL_LOGO';

function doGet() {
  return HtmlService.createHtmlOutputFromFile('Index')
    .setTitle('Firma de correo institucional')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

function correoUsuario() {
  return Session.getActiveUser().getEmail();
}

// Arma la firma en el servidor para que todas salgan con el mismo formato.
function firmaHtml(d) {
  d = d || {};
  const t = k => String(d[k] || '').trim().slice(0, 120)
    .replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const V = 'font-family:Verdana,Geneva,sans-serif;';
  const fono = [t('tel') && 'Telf.: ' + t('tel'), t('anexo') && 'Anexo: ' + t('anexo')].filter(Boolean).join('&nbsp;&nbsp;&nbsp;');
  const celu = t('cel') ? 'Cel.: ' + t('cel') : '';
  const fila = (txt, est) => txt ? `<tr><td colspan="2" style="${V}${est}padding:1px 0;">${txt}</td></tr>` : '';
  return `<table cellpadding="0" cellspacing="0" border="0" style="border-collapse:collapse;">
<tr>
<td style="vertical-align:middle;padding:0 14px 0 0;border-right:1px dotted #0077C8;">
<img src="${LOGO_URL}" alt="Logo" width="200" style="display:block;width:200px;height:auto;border:0;">
</td>
<td style="vertical-align:middle;padding:0 0 0 14px;">
<table cellpadding="0" cellspacing="0" border="0" style="border-collapse:collapse;">
<tr>
<td style="${V}font-size:12pt;font-weight:bold;color:#0077C8;padding:0 10px 2px 0;white-space:nowrap;">${t('nombre')}</td>
<td style="${V}font-size:9pt;font-weight:bold;color:#0077C8;padding:0 0 2px 10px;border-left:1px dotted #0077C8;text-transform:uppercase;white-space:nowrap;">${t('cargo')}</td>
</tr>
${fila(t('sub'), 'font-size:10pt;color:#0077C8;')}${fila(t('ofi'), 'font-size:12pt;color:#0077C8;')}${fila(fono, 'font-size:11pt;color:#7f7f7f;')}${fila(celu, 'font-size:11pt;color:#7f7f7f;')}
</table>
</td>
</tr>
</table>`;
}

// Guarda la firma en el Gmail de quien usa la aplicación.
function aplicarFirma(d) {
  if (!d || !String(d.nombre || '').trim() || !String(d.cargo || '').trim()) {
    throw new Error('Completa al menos tu nombre y tu cargo.');
  }
  const email = correoUsuario();
  try {
    Gmail.Users.Settings.SendAs.patch({ signature: firmaHtml(d) }, 'me', email);
  } catch (e) {
    // Pasa cuando al autorizar no se marcó la casilla de configuración de Gmail.
    if (/permis|authoriz|autoriz|scope|gmail\.settings/i.test(e.message)) {
      throw new Error('Falta autorizar el permiso de Gmail: recarga la página y, cuando Google pida permisos, marca todas las casillas.');
    }
    throw e;
  }
  return email;
}
