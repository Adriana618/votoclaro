'use client';

import Image from 'next/image';
import { useState } from 'react';

/** Maps party abbreviation → logo file in /logos/ */
const LOGO_FILES: Record<string, string> = {
  rp: '/logos/rp.png',
  fp: '/logos/fp.png',
  pm: '/logos/pm.png',
  jpp: '/logos/jpp.png',
  pl: '/logos/pl.png',
  app: '/logos/app.png',
  pod: '/logos/pod.png',
  sc: '/logos/sc.png',
  apra: '/logos/apra.png',
  avp: '/logos/avp.png',
  fep: '/logos/fep.png',
  frepap: '/logos/frepap.png',
  fyl: '/logos/fyl.png',
  un: '/logos/un.png',
  cp: '/logos/cp.png',
  an: '/logos/an.png',
  pte: '/logos/pte.png',
  ppt: '/logos/ppt.png',
  pdup: '/logos/pdup.png',
  id: '/logos/id.png',
  ucd: '/logos/ucd.png',
  pp: '/logos/pp.png',
  lp: '/logos/lp.png',
  pa: '/logos/pa.png',
  pdv: '/logos/pdv.png',
  prog: '/logos/prog.png',
  pbg: '/logos/pbg.png',
  prin: '/logos/prin.png',
  obras: '/logos/obras.png',
  plg: '/logos/plg.png',
  pdf: '/logos/pdf.png',
  salv: '/logos/salv.png',
  ppp: '/logos/ppp.png',
  fep2: '/logos/fep2.png',
  pmod: '/logos/pmod.png',
  sicreo: '/logos/sicreo.png',
  cpp: '/logos/cpp.png',
  venc: '/logos/venc.png',
};

interface PartyLogoProps {
  abbreviation: string;
  name?: string;
  color?: string;
  size?: number;
  className?: string;
}

export default function PartyLogo({
  abbreviation,
  name,
  color,
  size = 40,
  className = '',
}: PartyLogoProps) {
  const [imgError, setImgError] = useState(false);
  const logoSrc = LOGO_FILES[abbreviation?.toLowerCase()];

  if (logoSrc && !imgError) {
    return (
      <div
        className={`rounded-lg overflow-hidden bg-white flex items-center justify-center shrink-0 ${className}`}
        style={{ width: size, height: size }}
      >
        <Image
          src={logoSrc}
          alt={name || abbreviation}
          width={size}
          height={size}
          className="object-contain"
          onError={() => setImgError(true)}
          unoptimized
        />
      </div>
    );
  }

  // Fallback: colored square with first letter
  return (
    <div
      className={`rounded-lg flex items-center justify-center font-bold text-white shrink-0 ${className}`}
      style={{
        width: size,
        height: size,
        backgroundColor: color || '#374151',
        fontSize: size * 0.4,
      }}
    >
      {(name || abbreviation || '?').charAt(0).toUpperCase()}
    </div>
  );
}
