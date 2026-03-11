'use client';

import { MapPin } from 'lucide-react';

const PERU_REGIONS = [
  { id: 'amazonas', name: 'Amazonas' },
  { id: 'ancash', name: 'Áncash' },
  { id: 'apurimac', name: 'Apurímac' },
  { id: 'arequipa', name: 'Arequipa' },
  { id: 'ayacucho', name: 'Ayacucho' },
  { id: 'cajamarca', name: 'Cajamarca' },
  { id: 'callao', name: 'Callao' },
  { id: 'cusco', name: 'Cusco' },
  { id: 'huancavelica', name: 'Huancavelica' },
  { id: 'huanuco', name: 'Huánuco' },
  { id: 'ica', name: 'Ica' },
  { id: 'junin', name: 'Junín' },
  { id: 'la-libertad', name: 'La Libertad' },
  { id: 'lambayeque', name: 'Lambayeque' },
  { id: 'lima', name: 'Lima' },
  { id: 'lima-provincias', name: 'Lima Provincias' },
  { id: 'loreto', name: 'Loreto' },
  { id: 'madre-de-dios', name: 'Madre de Dios' },
  { id: 'moquegua', name: 'Moquegua' },
  { id: 'pasco', name: 'Pasco' },
  { id: 'piura', name: 'Piura' },
  { id: 'puno', name: 'Puno' },
  { id: 'san-martin', name: 'San Martín' },
  { id: 'tacna', name: 'Tacna' },
  { id: 'tumbes', name: 'Tumbes' },
  { id: 'ucayali', name: 'Ucayali' },
  { id: 'peruanos-en-el-extranjero', name: 'Peruanos en el Extranjero' },
];

interface RegionSelectorProps {
  value: string;
  onChange: (regionId: string) => void;
  label?: string;
  className?: string;
}

export default function RegionSelector({
  value,
  onChange,
  label = 'Selecciona tu región',
  className = '',
}: RegionSelectorProps) {
  return (
    <div className={className}>
      {label && (
        <label htmlFor="region-select" className="block text-sm font-medium text-gray-400 mb-2">
          <MapPin size={14} className="inline mr-1" />
          {label}
        </label>
      )}
      <select
        id="region-select"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-[#D4AF37] focus:ring-1 focus:ring-[#D4AF37] transition-colors appearance-none cursor-pointer"
      >
        <option value="">-- Elige una región --</option>
        {PERU_REGIONS.map((region) => (
          <option key={region.id} value={region.id}>
            {region.name}
          </option>
        ))}
      </select>
    </div>
  );
}
