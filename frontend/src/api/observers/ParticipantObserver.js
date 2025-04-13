/**
 * Observer that monitors participant selection/filtering
 */
export default class ParticipantObserver {
  constructor() {
    this.components = [];
  }
  
  /**
   * Add a component that should be updated when participant selection changes
   * @param {Object} component - Component that will receive updates
   */
  addComponent(component) {
    if (!this.components.includes(component)) {
      this.components.push(component);
    }
  }
  
  /**
   * Remove a component from update notifications
   * @param {Object} component - Component to remove
   */
  removeComponent(component) {
    const index = this.components.indexOf(component);
    if (index !== -1) {
      this.components.splice(index, 1);
    }
  }
  
  /**
   * Update method called by Observable when changes occur
   * @param {Object} data - Data containing participant information
   */
  update(data) {
    // Notify all registered components about the change
    this.components.forEach(component => {
      if (typeof component.onParticipantUpdate === 'function') {
        component.onParticipantUpdate(data);
      }
    });
  }
}
