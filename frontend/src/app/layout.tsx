import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Navigation from '@/components/Navigation';
import ServiceWorkerRegister from '@/components/ServiceWorkerRegister';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
});

export const metadata: Metadata = {
  title: 'VotoClaro - Que la ignorancia no gane las elecciones',
  description:
    'Herramienta de voto estratégico para las elecciones Perú 2026. Simula tu voto, descubre con quién coincides y conoce los datos que deberías saber antes de votar.',
  keywords: [
    'elecciones Perú 2026',
    'voto estratégico',
    'cifra repartidora',
    "D'Hondt",
    'congreso Perú',
    'partidos políticos Perú',
    'VotoClaro',
  ],
  openGraph: {
    title: 'VotoClaro - Voto Estratégico Perú 2026',
    description: 'Que la ignorancia no gane las elecciones. Simula, compara y comparte.',
    type: 'website',
    locale: 'es_PE',
    siteName: 'VotoClaro',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'VotoClaro - Voto Estratégico Perú 2026',
    description: 'Que la ignorancia no gane las elecciones.',
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <head>
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#D4AF37" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <link rel="apple-touch-icon" href="/icon-192.png" />
      </head>
      <body className={`${inter.variable} font-sans antialiased bg-gray-950 text-white`}>
        <ServiceWorkerRegister />
        <Navigation />
        <main className="min-h-screen pt-16">{children}</main>
        <footer className="border-t border-gray-800 py-8 px-4 text-center">
          <p className="text-[#D4AF37] font-semibold text-lg mb-2">
            Que la ignorancia no gane las elecciones
          </p>
          <p className="text-gray-500 text-sm">
            VotoClaro 2026 &mdash; Herramienta ciudadana, no partidaria.
          </p>
          <div className="mt-4 flex justify-center gap-6 text-sm text-gray-600">
            <a href="/privacidad" className="hover:text-gray-400 transition-colors">
              Privacidad
            </a>
            <a href="/aprende" className="hover:text-gray-400 transition-colors">
              Aprende
            </a>
          </div>
        </footer>
      </body>
    </html>
  );
}
