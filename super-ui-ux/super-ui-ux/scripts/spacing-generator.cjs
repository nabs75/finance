/**
 * Script utilitaire pour générer des échelles d'espacement (Spacing Scale)
 */
const generateSpacingScale = (base = 8, steps = 10) => {
  const scale = {};
  for (let i = 1; i <= steps; i++) {
    scale[`spacing-${i}`] = `${base * i}px`;
  }
  return scale;
};

console.log(JSON.stringify(generateSpacingScale(), null, 2));