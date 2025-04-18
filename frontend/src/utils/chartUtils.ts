export const extractChartData = (recommendation: any) => {
  if (!recommendation || !recommendation.cognitive_traits) return [];
  
  const traits = recommendation.cognitive_traits;
  return [
    { name: 'Analytical Thinking', value: traits.analytical_thinking ?? 0 },
    { name: 'Attention to Detail', value: traits.attention_to_detail ?? 0 },
    { name: 'Collaboration', value: traits.collaboration ?? 0 },
    { name: 'Adaptability', value: traits.adaptability ?? 0 },
    { name: 'Independence', value: traits.independence ?? 0 },
    { name: 'Evaluation', value: traits.evaluation ?? 0 },
    { name: 'Decision Making', value: traits.decision_making ?? 0 },
    { name: 'Stress Tolerance', value: traits.stress_tolerance ?? 0 }
  ];
}; 