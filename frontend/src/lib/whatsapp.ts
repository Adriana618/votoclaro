export function antiVoteMessage(
  region: string,
  rejectedLabel: string,
  recommendedParty: string
): string {
  return (
    `🗳️ *VotoClaro - Simulador de Voto Estratégico*\n\n` +
    `En *${region}*, si no quieres que gane *${rejectedLabel}*, ` +
    `tu mejor opción estratégica es votar por *${recommendedParty}*.\n\n` +
    `La cifra repartidora (D'Hondt) hace que dividir el voto entre partidos pequeños ` +
    `termine beneficiando a los que quieres evitar.\n\n` +
    `Calcula tu voto estratégico en 👉 votoclaro.pe/simulador\n\n` +
    `_Que la ignorancia no gane las elecciones 🇵🇪_`
  );
}

export function quizMessage(topMatch: string, matchPercent: number): string {
  return (
    `🎯 *VotoClaro - Test de Afinidad Política*\n\n` +
    `Según mis respuestas, el partido con el que más coincido es *${topMatch}* ` +
    `con un *${matchPercent}%* de afinidad.\n\n` +
    `¿Con quién coincides tú? Descúbrelo en 👉 votoclaro.pe/quiz\n\n` +
    `_Que la ignorancia no gane las elecciones 🇵🇪_`
  );
}

export function spicyFactMessage(fact: string): string {
  return (
    `🔥 *¿Sabías que...?*\n\n` +
    `${fact}\n\n` +
    `Más datos en 👉 votoclaro.pe/sabias-que\n\n` +
    `_VotoClaro - Que la ignorancia no gane las elecciones 🇵🇪_`
  );
}

export function whatsappUrl(message: string): string {
  return `https://wa.me/?text=${encodeURIComponent(message)}`;
}

export function shareOnWhatsApp(message: string): void {
  const url = whatsappUrl(message);
  if (typeof window !== 'undefined') {
    window.open(url, '_blank');
  }
}
