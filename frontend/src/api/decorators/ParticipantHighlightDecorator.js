import ChartDecorator from './ChartDecorator';

/**
 * Decorator that adds participant highlighting functionality to a chart
 */
export default class ParticipantHighlightDecorator extends ChartDecorator {
  constructor(chart, options = {}) {
    super(chart);
    this.options = {
      highlightedParticipantId: null,
      highlightColor: '#ff6b6b',
      regularColor: '#4682b4',
      dimOpacity: 0.3,
      ...options
    };
  }
  
  // Override render to add highlighting functionality
  render() {
    // First let the decorated chart render itself
    this.chart.render();
    
    // Then apply highlighting
    this.applyHighlighting();
  }
  
  applyHighlighting() {
    // Implementation depends on chart library and type
    // This is a placeholder implementation
    if (!this.options.highlightedParticipantId) {
      return; // No participant selected, nothing to highlight
    }
    
    console.log(`Highlighting participant: ${this.options.highlightedParticipantId}`);
    
    // Get chart elements and apply highlighting
    // The exact implementation would depend on the charting library used
  }
  
  /**
   * Update the highlighted participant
   * @param {string|number} participantId - The ID of the participant to highlight
   */
  setHighlightedParticipant(participantId) {
    this.options.highlightedParticipantId = participantId;
    this.render(); // Re-render with new highlighting
  }
  
  /**
   * Clear highlighting
   */
  clearHighlighting() {
    this.options.highlightedParticipantId = null;
    this.render(); // Re-render without highlighting
  }
}
