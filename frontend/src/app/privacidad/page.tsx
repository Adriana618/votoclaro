export default function PrivacidadPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-extrabold mb-8">
        Politica de <span className="text-[#D4AF37]">Privacidad</span>
      </h1>

      <div className="prose prose-invert prose-sm max-w-none space-y-6 text-gray-300">
        <section>
          <h2 className="text-xl font-bold text-white">1. Informacion que recopilamos</h2>
          <p>
            VotoClaro es una herramienta ciudadana que prioriza tu privacidad. Recopilamos la
            minima informacion necesaria para brindarte el servicio:
          </p>
          <ul className="list-disc pl-5 space-y-1">
            <li>
              <strong>DNI (opcional):</strong> Solo si te registras para alertas.
              Tu DNI <strong>nunca se almacena en texto plano</strong>. Se transforma
              inmediatamente en un hash criptografico irreversible (HMAC-SHA256 con clave
              secreta). Es imposible recuperar el DNI original a partir de este hash.
            </li>
            <li>
              <strong>Region electoral:</strong> Para personalizar las recomendaciones
              de voto estrategico en tu circunscripcion.
            </li>
            <li>
              <strong>Numero de telefono (opcional):</strong> Solo si autorizas recibir
              alertas. Se almacena como hash criptografico, igual que el DNI.
            </li>
            <li>
              <strong>Respuestas del quiz:</strong> Se procesan en tiempo real para
              calcular tu afinidad ideologica. No se almacenan asociadas a tu identidad.
            </li>
            <li>
              <strong>Preferencias de voto estrategico:</strong> Cuando usas el simulador,
              se guardan datos agregados (partido recomendado, region) para mostrar
              tendencias colectivas. Estos datos no estan vinculados a tu DNI ni identidad personal.
            </li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-bold text-white">2. Como protegemos tu DNI</h2>
          <p>
            Tu DNI es informacion sensible. Por eso aplicamos las siguientes medidas:
          </p>
          <ul className="list-disc pl-5 space-y-1">
            <li>
              Se aplica un hash criptografico HMAC-SHA256 con clave secreta del servidor
              inmediatamente al recibirlo. El DNI original nunca se escribe en disco ni
              en la base de datos.
            </li>
            <li>
              El hash resultante es irreversible: ni siquiera los administradores del
              sistema pueden recuperar tu DNI.
            </li>
            <li>
              La clave secreta utilizada para el hash se almacena de forma segura como
              variable de entorno del servidor, separada del codigo fuente.
            </li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-bold text-white">3. Como usamos tu informacion</h2>
          <ul className="list-disc pl-5 space-y-1">
            <li>Generar recomendaciones de voto estrategico personalizadas por region.</li>
            <li>Enviar alertas cuando la estrategia cambie en tu region (solo si te registraste).</li>
            <li>Generar estadisticas agregadas y anonimas sobre tendencias de voto.</li>
            <li>Mejorar los algoritmos de recomendacion con datos anonimizados.</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-bold text-white">4. Lo que NO hacemos</h2>
          <ul className="list-disc pl-5 space-y-1">
            <li>NO vendemos ni compartimos datos personales con terceros, bajo ninguna circunstancia.</li>
            <li>NO almacenamos tu DNI en texto plano ni en formato descifrable.</li>
            <li>NO compartimos datos con partidos politicos, campanas electorales ni entidades gubernamentales.</li>
            <li>NO rastreamos tu actividad fuera de VotoClaro.</li>
            <li>NO usamos cookies de publicidad, seguimiento ni analytics de terceros.</li>
            <li>NO estamos afiliados a ningun partido politico.</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-bold text-white">5. Seguridad</h2>
          <ul className="list-disc pl-5 space-y-1">
            <li>Todas las comunicaciones estan protegidas por HTTPS/TLS.</li>
            <li>Datos sensibles (DNI, telefono) se almacenan exclusivamente como hashes criptograficos irreversibles.</li>
            <li>Los endpoints sensibles tienen proteccion contra abuso mediante limitacion de solicitudes (rate limiting).</li>
            <li>Se aplican cabeceras de seguridad HTTP en todas las respuestas del servidor.</li>
            <li>El acceso a los servidores es restringido y auditado.</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-bold text-white">6. Retencion de datos</h2>
          <ul className="list-disc pl-5 space-y-1">
            <li>
              Los datos de registro (hash de DNI, hash de telefono, region) se conservan
              mientras el servicio este activo o hasta que solicites su eliminacion.
            </li>
            <li>
              Las respuestas del quiz no se almacenan de forma persistente; se procesan
              en memoria y se descartan.
            </li>
            <li>
              Los datos agregados de tendencias son anonimos y pueden conservarse
              indefinidamente con fines estadisticos e historicos.
            </li>
            <li>
              Despues del periodo electoral, los datos personales (hashes de DNI y
              telefono) seran eliminados en un plazo maximo de 90 dias.
            </li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-bold text-white">7. Tus derechos</h2>
          <p>
            De acuerdo con la Ley N.° 29733 (Ley de Proteccion de Datos Personales del Peru),
            tienes derecho a:
          </p>
          <ul className="list-disc pl-5 space-y-1">
            <li><strong>Acceso:</strong> Solicitar informacion sobre los datos que tenemos asociados a tu registro.</li>
            <li><strong>Eliminacion:</strong> Solicitar la eliminacion completa e irreversible de tu registro y todos los datos asociados.</li>
            <li><strong>Revocacion:</strong> Dejar de recibir alertas en cualquier momento.</li>
            <li><strong>Rectificacion:</strong> Corregir los datos de tu registro (region, preferencias de alerta).</li>
            <li><strong>Oposicion:</strong> Oponerte al procesamiento de tus datos en cualquier momento.</li>
          </ul>
          <p>
            Para ejercer cualquiera de estos derechos, contactanos al correo indicado abajo.
            Responderemos en un plazo maximo de 10 dias habiles.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-white">8. Datos agregados</h2>
          <p>
            Las tendencias colectivas que mostramos en el panel de tendencias son completamente
            anonimas. No es posible identificar a ningun usuario individual a partir de los
            datos agregados. Estos datos se utilizan exclusivamente para informar al electorado
            sobre patrones de voto estrategico.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-white">9. Cambios a esta politica</h2>
          <p>
            Nos reservamos el derecho de actualizar esta politica de privacidad. Cualquier
            cambio sera publicado en esta pagina con la fecha de actualizacion correspondiente.
            Si los cambios son significativos, notificaremos a los usuarios registrados.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-white">10. Contacto</h2>
          <p>
            Para consultas sobre privacidad, ejercer tus derechos o reportar incidentes
            de seguridad, escribenos a{' '}
            <a href="mailto:privacidad@votaclaro.com" className="text-[#D4AF37] hover:underline">
              privacidad@votaclaro.com
            </a>
          </p>
        </section>

        <p className="text-gray-500 text-xs mt-8">
          Ultima actualizacion: Marzo 2026
        </p>
      </div>
    </div>
  );
}
