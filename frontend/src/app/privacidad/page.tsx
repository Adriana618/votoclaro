export default function PrivacidadPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-extrabold mb-8">
        🔒 Política de <span className="text-[#D4AF37]">Privacidad</span>
      </h1>

      <div className="prose prose-invert prose-sm max-w-none space-y-6 text-gray-300">
        <section>
          <h2 className="text-xl font-bold text-white">1. Información que recopilamos</h2>
          <p>
            VotoClaro es una herramienta ciudadana que prioriza tu privacidad. Recopilamos la
            mínima información necesaria:
          </p>
          <ul className="list-disc pl-5 space-y-1">
            <li><strong>DNI (opcional):</strong> Solo si te registras para alertas. Se almacena encriptado con AES-256 y nunca se muestra en texto plano.</li>
            <li><strong>Región electoral:</strong> Para personalizar las recomendaciones.</li>
            <li><strong>Número de WhatsApp (opcional):</strong> Solo para enviar alertas si tú lo autorizas.</li>
            <li><strong>Respuestas del quiz:</strong> Se procesan en tiempo real y no se asocian a tu identidad.</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-bold text-white">2. Cómo usamos tu información</h2>
          <ul className="list-disc pl-5 space-y-1">
            <li>Generar recomendaciones de voto estratégico personalizadas.</li>
            <li>Enviar alertas cuando la estrategia cambie en tu región (solo si te registraste).</li>
            <li>Generar estadísticas agregadas y anónimas sobre tendencias de voto.</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-bold text-white">3. Lo que NO hacemos</h2>
          <ul className="list-disc pl-5 space-y-1">
            <li>NO vendemos ni compartimos datos personales con terceros.</li>
            <li>NO almacenamos tu DNI en texto plano.</li>
            <li>NO rastreamos tu actividad fuera de VotoClaro.</li>
            <li>NO usamos cookies de publicidad o seguimiento.</li>
            <li>NO estamos afiliados a ningún partido político.</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-bold text-white">4. Seguridad</h2>
          <p>
            Todos los datos sensibles se encriptan en tránsito (HTTPS/TLS) y en reposo (AES-256).
            Los servidores están protegidos y el acceso es restringido.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-white">5. Tus derechos</h2>
          <p>Puedes solicitar en cualquier momento:</p>
          <ul className="list-disc pl-5 space-y-1">
            <li>Acceso a tus datos personales almacenados.</li>
            <li>Eliminación completa de tu registro.</li>
            <li>Dejar de recibir alertas.</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-bold text-white">6. Datos agregados</h2>
          <p>
            Las tendencias colectivas que mostramos son completamente anónimas. No es posible
            identificar a ningún usuario individual a partir de los datos agregados.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-white">7. Contacto</h2>
          <p>
            Para consultas sobre privacidad, escríbenos a{' '}
            <a href="mailto:privacidad@votoclaro.pe" className="text-[#D4AF37] hover:underline">
              privacidad@votoclaro.pe
            </a>
          </p>
        </section>

        <p className="text-gray-500 text-xs mt-8">
          Última actualización: Marzo 2026
        </p>
      </div>
    </div>
  );
}
