/**
 * Base Repository class for data access
 */
export default class Repository {
  constructor() {
    if (this.constructor === Repository) {
      throw new Error('Repository is an abstract class and cannot be instantiated directly');
    }
  }
  
  /**
   * Fetch all items
   * @returns {Promise<Array>} Promise resolving to array of items
   */
  async findAll() {
    throw new Error('Method findAll() must be implemented by subclass');
  }
  
  /**
   * Find an item by ID
   * @param {string|number} id - The ID of the item to find
   * @returns {Promise<Object>} Promise resolving to the found item
   */
  async findById(id) {
    throw new Error('Method findById() must be implemented by subclass');
  }
  
  /**
   * Save an item
   * @param {Object} item - The item to save
   * @returns {Promise<Object>} Promise resolving to the saved item
   */
  async save(item) {
    throw new Error('Method save() must be implemented by subclass');
  }
  
  /**
   * Delete an item
   * @param {string|number} id - The ID of the item to delete
   * @returns {Promise<boolean>} Promise resolving to success status
   */
  async delete(id) {
    throw new Error('Method delete() must be implemented by subclass');
  }
}
