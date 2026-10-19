export const CANDIDATES = [
  {word: 'mat', value: 62, color: '#78E8D8'},
  {word: 'floor', value: 20, color: '#6CA8FF'},
  {word: 'bed', value: 12, color: '#A8C7FF'},
  {word: 'moon', value: 6, color: '#F2B56B'},
] as const;

export const SENTENCE = ['The', 'cat', 'sat', 'on', 'the'] as const;

export const CAPTION_LINES: Record<string, string> = {
  p1: 'Next-token prediction is\nbeautifully simple.',
  p2: 'The model reads the pieces so far:\n“The cat sat on the…”',
  p3: 'Then it scores every possible\nnext piece.',
  p4: 'Think of a weighted ballot:\nmat leads, then floor, bed, and moon.',
  p5: 'One piece is chosen\nand added.',
  p6: 'Predict. Place. Repeat.',
  p7: 'Likely wording is not\nguaranteed truth.',
};
