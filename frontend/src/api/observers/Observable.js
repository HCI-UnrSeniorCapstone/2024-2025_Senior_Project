/**
 * Observable base class for implementing the Observer pattern
 */
export default class Observable {
  constructor() {
    this.observers = [];
  }
  
  /**
   * Add an observer to the notification list
   * @param {Object} observer - The observer to add
   */
  addObserver(observer) {
    // Ensure observer has update method
    if (typeof observer.update !== 'function') {
      throw new Error('Observer must implement update method');
    }
    
    // Add observer if not already in the list
    if (!this.observers.includes(observer)) {
      this.observers.push(observer);
    }
  }
  
  /**
   * Remove an observer from the notification list
   * @param {Object} observer - The observer to remove
   */
  removeObserver(observer) {
    const index = this.observers.indexOf(observer);
    if (index !== -1) {
      this.observers.splice(index, 1);
    }
  }
  
  /**
   * Notify all observers of a change
   * @param {*} data - Data to pass to observers
   */
  notifyObservers(data) {
    this.observers.forEach(observer => {
      observer.update(data);
    });
  }
}
