# Genera las capturas de docs/ cargando la página real (src/Index.html) con datos ficticios.
# Reemplaza google.script.run por respuestas simuladas; no se conecta a Google.
# Uso: python docs/capturas/generar.py   (necesita Google Chrome instalado)
import pathlib, subprocess, tempfile, shutil, os

RAIZ = pathlib.Path(__file__).resolve().parents[2]
CHROME = next((c for c in [r'C:/Program Files/Google/Chrome/Application/chrome.exe',
                           '/usr/bin/google-chrome', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']
               if os.path.exists(c)), shutil.which('chrome') or 'chrome')
LOGO = ("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='46'>"
        "<rect width='200' height='46' rx='6' fill='%23e3f0fa'/><text x='100' y='30' font-family='Verdana' "
        "font-size='16' fill='%230077C8' text-anchor='middle'>LOGO</text></svg>")
FIRMA = f"""<table cellpadding="0" cellspacing="0" style="border-collapse:collapse"><tr>
<td style="padding:0 14px 0 0;border-right:1px dotted #0077C8"><img src="{LOGO}" width="200"></td>
<td style="padding:0 0 0 14px;font-family:Verdana"><table cellpadding="0" cellspacing="0"><tr>
<td style="font-size:12pt;font-weight:bold;color:#0077C8;padding:0 10px 2px 0">Ana María Torres Quispe</td>
<td style="font-size:9pt;font-weight:bold;color:#0077C8;padding:0 0 2px 10px;border-left:1px dotted #0077C8">TÉCNICA ASISTENCIAL</td></tr>
<tr><td colspan="2" style="font-size:10pt;color:#0077C8">Unidad de Ejemplo</td></tr>
<tr><td colspan="2" style="font-size:12pt;color:#0077C8">Hospital de Ejemplo</td></tr></table></td></tr></table>"""

# estado: (permiso concedido, pulsar "Aplicar" al cargar)
CAPTURAS = {'formulario': (True, True), 'aviso-permiso': (False, False)}

def stub(ok, aplicar):
    datos = {'nombre': 'Ana María Torres Quispe', 'cargo': 'Técnica asistencial',
             'sub': 'Unidad de Ejemplo', 'ofi': 'Hospital de Ejemplo'}
    return f"""<script>
const R={{estadoPermiso:{{ok:{str(ok).lower()},url:'#',recargar:'#'}},
 inicio:{{email:'ana.torres@ejemplo.pe',version:'1.1.0',hospital:'',nombre:'Firma de correo institucional'}},
 firmaHtml:{FIRMA!r}, aplicarFirma:'ana.torres@ejemplo.pe'}};
function Run(s,f){{this.s=s;this.f=f}}
Run.prototype.withSuccessHandler=function(s){{return new Run(s,this.f)}};
Run.prototype.withFailureHandler=function(f){{return new Run(this.s,f)}};
Object.keys(R).forEach(k=>Run.prototype[k]=function(){{const s=this.s;setTimeout(()=>s&&s(R[k]),10)}});
window.google={{script:{{run:new Run()}}}};
window.addEventListener('load',()=>setTimeout(()=>{{
  const d={datos!r}; for (const k in d) document.querySelector('[name='+k+']').value=d[k];
  {"document.getElementById('aplicar').click();" if aplicar else ''}
}},100));
</script>"""

html = (RAIZ / 'src' / 'Index.html').read_text(encoding='utf-8')
with tempfile.TemporaryDirectory() as tmp:
    for nombre, (ok, aplicar) in CAPTURAS.items():
        pagina = pathlib.Path(tmp) / f'{nombre}.html'
        pagina.write_text(html.replace('<script>', stub(ok, aplicar) + '<script>', 1), encoding='utf-8')
        subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1',
                        '--virtual-time-budget=3000', '--window-size=820,' + ('900' if ok else '420'),
                        f'--screenshot={RAIZ / "docs" / (nombre + ".png")}', pagina.as_uri()],
                       check=True, capture_output=True)
        print('docs/' + nombre + '.png')
